import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
from config.materials import materials
from core.constraints import clamp_curve
from core.gradation_engine import GradationEngine

class GraphPanel(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="#0f172a", corner_radius=15)

        self.material_key = "fine"
        self.data = materials[self.material_key]

        # Get shared total weight manager from parent app
        self.grad_engine = GradationEngine(parent.total_weight_manager)

        self.sieve_sizes = []
        self.sieve_labels = []
        self.lower = []
        self.upper = []
        self.obtained = []

        self.drag_index = None
        self.selected_index = None  # Track which point is selected
        self.updating_from_table = False  # Flag to prevent circular updates

        self._build_graph()
        self._build_controls()

    # ----------------------------------------------------
    # BUILD GRAPH UI
    # ----------------------------------------------------

    def _build_graph(self):
        self.figure, self.ax = plt.subplots(figsize=(7,5), dpi=100)
        self.figure.patch.set_facecolor('#0f172a')
        self.ax.set_facecolor('#0f172a')

        self.ax.tick_params(colors="#94a3b8", labelsize=9, length=4, width=0.5)
        self.ax.spines["bottom"].set_color("#334155")
        self.ax.spines["left"].set_color("#334155")
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)

        self.ax.set_xlabel("Sieve Size (mm)", color="#94a3b8", fontsize=11)
        self.ax.set_ylabel("% Passing", color="#94a3b8", fontsize=11)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas.mpl_connect("button_press_event", self._on_click)
        self.canvas.mpl_connect("motion_notify_event", self._on_drag)
        self.canvas.mpl_connect("button_release_event", self._on_release)
        self.canvas.mpl_connect("key_press_event", self._on_mpl_key_press)  # Matplotlib key events
        
        # Bind keyboard events at the Tkinter level (parent window)
        self.master.bind("<Up>", self._on_key_up_tkinter, add=True)
        self.master.bind("<Down>", self._on_key_down_tkinter, add=True)

    def _build_controls(self):
        """Build control panel for precise point adjustment"""
        control_frame = ctk.CTkFrame(self, fg_color="#252d3d", corner_radius=8)
        control_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        label = ctk.CTkLabel(control_frame, text="Selected Point Value:", font=("Segoe UI", 11))
        label.pack(side="left", padx=(10, 5), pady=8)
        
        self.point_value_entry = ctk.CTkEntry(
            control_frame, 
            width=80, 
            placeholder_text="Click point",
            font=("Segoe UI", 11),
            fg_color="#1a1f2e",
            border_color="#0891b2",
            border_width=1
        )
        self.point_value_entry.pack(side="left", padx=5, pady=8)
        self.point_value_entry.bind("<Return>", self._on_entry_confirm)
        self.point_value_entry.bind("<Up>", self._on_entry_key_up)
        self.point_value_entry.bind("<Down>", self._on_entry_key_down)
        
        info_label = ctk.CTkLabel(
            control_frame, 
            text="(Use ↑↓ keys or edit & press Enter)", 
            font=("Segoe UI", 10, "italic"),
            text_color="#94a3b8"
        )
        info_label.pack(side="left", padx=10, pady=8)

    # ----------------------------------------------------
    # LOAD MATERIAL LIMITS + SETUP
    # ----------------------------------------------------

    def load_material(self, material_key):
        self.material_key = material_key
        self.data = materials[material_key]

        # Load sieve data from config and REVERSE for left-to-right display (small to large)
        sieve_labels = list(reversed(self.data["sieve_sizes"]))
        lower_limits = np.array(list(reversed(self.data["lower_limits"])), dtype=float)
        upper_limits = np.array(list(reversed(self.data["upper_limits"])), dtype=float)
        
        n = len(sieve_labels)
        self.sieve_sizes = np.arange(n)  # 0, 1, 2, ... for x-axis positions
        self.sieve_labels = sieve_labels  # Store labels for display (small to large: left to right)
        self.lower = lower_limits
        self.upper = upper_limits
        # Initialize obtained curve with midpoint between upper and lower limits
        self.obtained = (self.lower + self.upper) / 2

        self._redraw_graph()

    # ----------------------------------------------------
    # DRAW GRAPH
    # ----------------------------------------------------

    def _redraw_graph(self):
        """Redraws the entire graph with current data"""
        self.ax.clear()
        self.ax.set_facecolor('#0f172a')
        self.ax.tick_params(colors="#94a3b8", labelsize=9, length=4, width=0.5)
        self.ax.spines["bottom"].set_color("#334155")
        self.ax.spines["left"].set_color("#334155")
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)

        # Subtle grid
        self.ax.grid(True, alpha=0.12, color="#475569", linestyle="-", linewidth=0.5)
        self.ax.set_axisbelow(True)

        n = len(self.sieve_sizes)

        # Create smooth interpolation for curves
        if n > 2:
            x_smooth = np.linspace(0, n - 1, n * 10)
            lower_smooth = np.interp(x_smooth, self.sieve_sizes, self.lower)
            upper_smooth = np.interp(x_smooth, self.sieve_sizes, self.upper)
            obtained_smooth = np.interp(x_smooth, self.sieve_sizes, self.obtained)
        else:
            x_smooth = self.sieve_sizes
            lower_smooth = self.lower
            upper_smooth = self.upper
            obtained_smooth = self.obtained

        # Shaded grading envelope
        self.ax.fill_between(x_smooth, lower_smooth, upper_smooth, alpha=0.07, color="#0ea5e9", linewidth=0)

        # Limit curves
        self.ax.plot(x_smooth, lower_smooth, color="#64748b", linewidth=1.5, linestyle="--", alpha=0.6, label="Lower Limit")
        self.ax.plot(x_smooth, upper_smooth, color="#64748b", linewidth=1.5, linestyle="--", alpha=0.6, label="Upper Limit")

        # Obtained curve with glow effect
        self.ax.plot(x_smooth, obtained_smooth, color="#0ea5e9", linewidth=5, alpha=0.12, zorder=2)
        self.ax.plot(x_smooth, obtained_smooth, color="#06b6d4", linewidth=2.5, label="Obtained", zorder=3)

        # Draggable points with selected-point highlight
        for i in range(n):
            if i == self.selected_index:
                self.ax.scatter(self.sieve_sizes[i], self.obtained[i],
                    color="#f59e0b", s=130, edgecolor="#fbbf24", zorder=6, linewidth=2.5)
            else:
                self.ax.scatter(self.sieve_sizes[i], self.obtained[i],
                    color="#22d3ee", s=80, edgecolor="white", zorder=5, linewidth=1.5)

        # Smart sieve labels
        def fmt_sieve(x):
            if isinstance(x, str):
                return x
            if x >= 10:
                return f"{x:.0f}"
            if x >= 1:
                return f"{x:.1f}"
            return f"{x:.2f}"

        self.ax.set_xticks(self.sieve_sizes)
        self.ax.set_xticklabels([fmt_sieve(x) for x in self.sieve_labels], rotation=45, ha='right', fontsize=9)
        self.ax.set_xlabel("Sieve Size (mm)", color="#94a3b8", fontsize=11, labelpad=8)
        self.ax.set_ylabel("% Passing", color="#94a3b8", fontsize=11, labelpad=8)

        self.ax.legend(
            facecolor="#1e293b", edgecolor="#334155", labelcolor="#94a3b8",
            loc='upper left', framealpha=0.95, fontsize=9
        )
        self.ax.set_ylim(-5, 110)
        self.figure.tight_layout(pad=1.2)

        self.canvas.draw()

    def _fast_update_curve(self):
        """Fast update during dragging — full redraw for consistent visuals with selection highlight"""
        self._redraw_graph()

    # ----------------------------------------------------
    # DRAGGING LOGIC
    # ----------------------------------------------------

    def _on_click(self, event):
        if event.inaxes != self.ax:
            return

        # find nearest point
        distances = np.abs(self.sieve_sizes - event.xdata)
        index = distances.argmin()

        # confirm click within draggable radius
        if abs(self.obtained[index] - event.ydata) < 6:
            self.drag_index = index
            self.selected_index = index  # Track selection for keyboard control
            self._update_entry_field()  # Update the input field to show this point's value

    def _on_drag(self, event):
        if self.drag_index is None:
            return
        if event.inaxes != self.ax:
            return

        # clamp inside limits
        y = event.ydata
        y = max(self.lower[self.drag_index], min(self.upper[self.drag_index], y))

        self.obtained[self.drag_index] = y
        self._update_entry_field()  # Update field during drag

        # Update retained + table
        self._sync_back()

        # Fast redraw - only update the curve line and points without full layout recalculation
        self._fast_update_curve()

    def _on_release(self, event):
        self.drag_index = None

    def _on_key_up(self, event):
        """Handle Up arrow key to increase selected point's passing %"""
        if self.selected_index is not None:
            # Increase passing % by 0.1
            new_val = self.obtained[self.selected_index] + 0.1
            new_val = max(self.lower[self.selected_index], min(self.upper[self.selected_index], new_val))
            self.obtained[self.selected_index] = new_val
            self._update_entry_field()
            self._sync_back()
            self._redraw_graph()

    def _on_key_down(self, event):
        """Handle Down arrow key to decrease selected point's passing %"""
        if self.selected_index is not None:
            # Decrease passing % by 0.1
            new_val = self.obtained[self.selected_index] - 0.1
            new_val = max(self.lower[self.selected_index], min(self.upper[self.selected_index], new_val))
            self.obtained[self.selected_index] = new_val
            self._update_entry_field()
            self._sync_back()
            self._redraw_graph()

    def _on_key_up_tkinter(self, event):
        """Tkinter version of Up arrow handler"""
        return self._on_key_up(event)

    def _on_key_down_tkinter(self, event):
        """Tkinter version of Down arrow handler"""
        return self._on_key_down(event)

    def _on_mpl_key_press(self, event):
        """Handle matplotlib key press events"""
        if event.key == "up":
            self._on_key_up(event)
        elif event.key == "down":
            self._on_key_down(event)

    def _update_entry_field(self):
        """Update the input field to show the selected point's value"""
        if self.selected_index is not None:
            sieve_label = self.sieve_labels[self.selected_index]
            value = self.obtained[self.selected_index]
            self.point_value_entry.delete(0, "end")
            self.point_value_entry.insert(0, f"{value:.1f}% ({sieve_label}mm)")
            # Focus on entry field so keyboard events work
            self.point_value_entry.focus()

    def _on_entry_confirm(self, event):
        """Handle Enter key in the input field to set point value directly"""
        if self.selected_index is None:
            return
        
        try:
            # Parse the input (handle "XX.X% (mm)" format or just "XX.X")
            text = self.point_value_entry.get()
            value = float(text.split("%")[0].strip())
        except:
            return
        
        # Clamp to limits
        value = max(self.lower[self.selected_index], min(self.upper[self.selected_index], value))
        self.obtained[self.selected_index] = value
        self._update_entry_field()
        self._sync_back()
        self._redraw_graph()

    def _on_entry_key_up(self, event):
        """Handle Up arrow key in entry field"""
        if self.selected_index is not None:
            new_val = self.obtained[self.selected_index] + 0.1
            new_val = max(self.lower[self.selected_index], min(self.upper[self.selected_index], new_val))
            self.obtained[self.selected_index] = new_val
            self._update_entry_field()
            self._sync_back()
            self._redraw_graph()
        return "break"  # Prevent default behavior

    def _on_entry_key_down(self, event):
        """Handle Down arrow key in entry field"""
        if self.selected_index is not None:
            new_val = self.obtained[self.selected_index] - 0.1
            new_val = max(self.lower[self.selected_index], min(self.upper[self.selected_index], new_val))
            self.obtained[self.selected_index] = new_val
            self._update_entry_field()
            self._sync_back()
            self._redraw_graph()
        return "break"  # Prevent default behavior

    # ----------------------------------------------------
    # SYNC TO TABLE + FM
    # ----------------------------------------------------

    def _sync_back(self):
        # Skip if we're updating from table (prevent circular updates)
        if self.updating_from_table:
            return
            
        parent = self.master

        # Reverse obtained curve from graph order (small to large) back to table order (large to small)
        table_passing = list(reversed(self.obtained))
        
        # Calculate retained based on passing
        retained = self.grad_engine.passing_to_retained(table_passing)

        # Update both passing and retained in table atomically
        parent.table_panel.passing = table_passing
        parent.table_panel.retained = retained
        parent.table_panel._refresh_table()

        # update FM
        parent.input_panel.update_fm(retained)

    # ----------------------------------------------------

    def update_curve(self, new_curve):
        """Update curve from table edits"""
        # new_curve is in table order (largest to smallest)
        # Reverse to graph order (smallest to largest for left-to-right display)
        self.obtained = np.array(list(reversed(new_curve)), dtype=float)
        self.updating_from_table = True
        self._redraw_graph()
        self.updating_from_table = False