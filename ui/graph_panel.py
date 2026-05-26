import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import time
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

        # Precision controls
        self.snap_enabled = False
        self.snap_value = 0.5  # Snap to nearest 0.5%
        self.step_size = 0.1   # Arrow key step size
        self.shift_held = False  # Track shift key for precision mode

        # Drag tracking for precision mode
        self._drag_start_y = None
        self._drag_start_value = None

        # Throttle redraws during drag (target ~60fps)
        self._last_draw_time = 0
        self._min_draw_interval = 0.016  # ~60fps

        # Blitting support — artist references
        self._obtained_line = None
        self._obtained_glow = None
        self._scatter_artists = []
        self._background = None

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
        self.canvas.mpl_connect("key_press_event", self._on_mpl_key_press)

        # Bind keyboard events at the Tkinter level (parent window)
        self.master.bind("<Up>", self._on_key_up_tkinter, add=True)
        self.master.bind("<Down>", self._on_key_down_tkinter, add=True)
        self.master.bind("<Shift_L>", lambda e: self._set_shift(True), add=True)
        self.master.bind("<Shift_R>", lambda e: self._set_shift(True), add=True)
        self.master.bind("<KeyRelease-Shift_L>", lambda e: self._set_shift(False), add=True)
        self.master.bind("<KeyRelease-Shift_R>", lambda e: self._set_shift(False), add=True)

    def _set_shift(self, held):
        self.shift_held = held

    def _build_controls(self):
        """Build control panel for precise point adjustment"""
        control_frame = ctk.CTkFrame(self, fg_color="#252d3d", corner_radius=8)
        control_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Row 1: Selected point value
        row1 = ctk.CTkFrame(control_frame, fg_color="transparent")
        row1.pack(fill="x", padx=10, pady=(8, 4))
        
        label = ctk.CTkLabel(row1, text="Selected Point:", font=("Segoe UI", 11))
        label.pack(side="left", padx=(0, 5))
        
        self.point_value_entry = ctk.CTkEntry(
            row1, 
            width=100, 
            placeholder_text="Click point",
            font=("Segoe UI", 11),
            fg_color="#1a1f2e",
            border_color="#0891b2",
            border_width=1
        )
        self.point_value_entry.pack(side="left", padx=5)
        self.point_value_entry.bind("<Return>", self._on_entry_confirm)
        self.point_value_entry.bind("<Up>", self._on_entry_key_up)
        self.point_value_entry.bind("<Down>", self._on_entry_key_down)
        
        # Row 2: Precision controls
        row2 = ctk.CTkFrame(control_frame, fg_color="transparent")
        row2.pack(fill="x", padx=10, pady=(0, 8))
        
        # Snap toggle
        self.snap_var = ctk.BooleanVar(value=False)
        self.snap_check = ctk.CTkCheckBox(
            row2, text="Snap", font=("Segoe UI", 10),
            variable=self.snap_var,
            command=self._on_snap_toggle,
            fg_color="#0891b2", hover_color="#06b6d4",
            width=20, height=20,
            checkbox_width=18, checkbox_height=18
        )
        self.snap_check.pack(side="left", padx=(0, 5))
        
        # Snap value selector
        self.snap_selector = ctk.CTkOptionMenu(
            row2, values=["0.1", "0.5", "1.0", "5.0"],
            width=65, height=24,
            font=("Segoe UI", 10),
            fg_color="#1a1f2e", button_color="#0891b2",
            command=self._on_snap_value_change
        )
        self.snap_selector.set("0.5")
        self.snap_selector.pack(side="left", padx=(0, 10))
        
        # Step size label + selector
        step_label = ctk.CTkLabel(row2, text="Step:", font=("Segoe UI", 10), text_color="#94a3b8")
        step_label.pack(side="left", padx=(0, 3))
        
        self.step_selector = ctk.CTkOptionMenu(
            row2, values=["0.1", "0.5", "1.0", "5.0"],
            width=65, height=24,
            font=("Segoe UI", 10),
            fg_color="#1a1f2e", button_color="#0891b2",
            command=self._on_step_change
        )
        self.step_selector.set("0.1")
        self.step_selector.pack(side="left", padx=(0, 10))
        
        # Info text
        info_label = ctk.CTkLabel(
            row2, 
            text="Hold Shift = 10× precision", 
            font=("Segoe UI", 9, "italic"),
            text_color="#64748b"
        )
        info_label.pack(side="right", padx=5)

    def _on_snap_toggle(self):
        self.snap_enabled = self.snap_var.get()

    def _on_snap_value_change(self, val):
        try:
            self.snap_value = float(val)
        except:
            self.snap_value = 0.5

    def _on_step_change(self, val):
        try:
            self.step_size = float(val)
        except:
            self.step_size = 0.1

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

        # Reset selection
        self.selected_index = None
        self.drag_index = None
        self._background = None

        self._redraw_graph()

    # ----------------------------------------------------
    # HELPER: Get locked indices in graph order
    # ----------------------------------------------------

    def _get_locked_graph_indices(self):
        """Convert table-order locked rows to graph-order indices."""
        parent = self.master
        if not hasattr(parent, 'table_panel'):
            return set()
        
        locked_table = parent.table_panel.locked_rows
        n = len(self.obtained)
        # Graph order is reversed from table order
        # table index i → graph index (n-1-i)
        return {(n - 1 - i) for i in locked_table}

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
        if n == 0:
            self.canvas.draw_idle()
            return

        locked_graph = self._get_locked_graph_indices()

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

        # Obtained curve with glow effect (hidden initially for background capture)
        self._obtained_glow, = self.ax.plot(x_smooth, obtained_smooth, color="#0ea5e9", linewidth=5, alpha=0.12, zorder=2, visible=False)
        self._obtained_line, = self.ax.plot(x_smooth, obtained_smooth, color="#06b6d4", linewidth=2.5, label="Obtained", zorder=3, visible=False)

        # Draggable points with selection + lock highlighting
        self._scatter_artists = []
        for i in range(n):
            is_locked = i in locked_graph
            is_selected = (i == self.selected_index)
            
            if is_locked:
                # Locked point — red ring, can't be dragged
                artist = self.ax.scatter(self.sieve_sizes[i], self.obtained[i],
                    color="#ef4444", s=100, edgecolor="#fca5a5", zorder=6, linewidth=2.5,
                    marker='s', visible=False)
            elif is_selected:
                # Selected point — gold highlight
                artist = self.ax.scatter(self.sieve_sizes[i], self.obtained[i],
                    color="#f59e0b", s=130, edgecolor="#fbbf24", zorder=6, linewidth=2.5, visible=False)
            else:
                # Normal point
                artist = self.ax.scatter(self.sieve_sizes[i], self.obtained[i],
                    color="#22d3ee", s=80, edgecolor="white", zorder=5, linewidth=1.5, visible=False)
            self._scatter_artists.append(artist)

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

        # Draw normally
        self._obtained_glow.set_visible(True)
        self._obtained_line.set_visible(True)
        for artist in self._scatter_artists:
            artist.set_visible(True)
            
        self.canvas.draw()

    def _fast_update_curve(self):
        """
        Fast update during dragging using blitting.
        Only redraws the dynamic artists (obtained line + scatter points).
        Falls back to full redraw if background cache is missing.
        """
        n = len(self.sieve_sizes)
        if n == 0:
            return

        now = time.time()
        if (now - self._last_draw_time) < self._min_draw_interval:
            return  # Throttle: skip this frame
        self._last_draw_time = now

        # If we have a cached background, use blitting
        if self._background is not None and self._obtained_line is not None:
            try:
                # Restore background
                self.canvas.restore_region(self._background)

                # Update obtained curve data
                if n > 2:
                    x_smooth = np.linspace(0, n - 1, n * 10)
                    obtained_smooth = np.interp(x_smooth, self.sieve_sizes, self.obtained)
                else:
                    obtained_smooth = self.obtained

                self._obtained_glow.set_ydata(obtained_smooth)
                self._obtained_line.set_ydata(obtained_smooth)

                # Redraw dynamic artists
                self.ax.draw_artist(self._obtained_glow)
                self.ax.draw_artist(self._obtained_line)

                # Update scatter points
                locked_graph = self._get_locked_graph_indices()
                for i, artist in enumerate(self._scatter_artists):
                    artist.set_offsets([[self.sieve_sizes[i], self.obtained[i]]])

                    is_locked = i in locked_graph
                    is_selected = (i == self.selected_index)

                    if is_locked:
                        artist.set_facecolor("#ef4444")
                        artist.set_edgecolor("#fca5a5")
                        artist.set_sizes([100])
                    elif is_selected:
                        artist.set_facecolor("#f59e0b")
                        artist.set_edgecolor("#fbbf24")
                        artist.set_sizes([130])
                    else:
                        artist.set_facecolor("#22d3ee")
                        artist.set_edgecolor("white")
                        artist.set_sizes([80])

                    self.ax.draw_artist(artist)

                # Blit the updated region
                self.canvas.blit(self.ax.bbox)
                return

            except Exception:
                pass  # Fall through to full redraw

        # Fallback: full redraw
        self._redraw_graph()

    # ----------------------------------------------------
    # SNAP HELPER
    # ----------------------------------------------------

    def _apply_snap(self, value):
        """Apply snap-to-grid if enabled."""
        if self.snap_enabled and self.snap_value > 0:
            return round(value / self.snap_value) * self.snap_value
        return value

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
            locked_graph = self._get_locked_graph_indices()
            
            # Don't allow dragging locked points
            if index in locked_graph:
                # Still select it to show info, but don't set drag_index
                self.selected_index = index
                self._update_entry_field()
                self._redraw_graph()
                return
            
            # Capture clean background for blitting NOW, right before drag starts
            self._obtained_glow.set_visible(False)
            self._obtained_line.set_visible(False)
            for artist in self._scatter_artists:
                artist.set_visible(False)
                
            self.canvas.draw()
            self._background = self.canvas.copy_from_bbox(self.ax.bbox)
            
            self._obtained_glow.set_visible(True)
            self._obtained_line.set_visible(True)
            for artist in self._scatter_artists:
                artist.set_visible(True)
                
            self.ax.draw_artist(self._obtained_glow)
            self.ax.draw_artist(self._obtained_line)
            for artist in self._scatter_artists:
                self.ax.draw_artist(artist)
            self.canvas.blit(self.ax.bbox)

            self.drag_index = index
            self.selected_index = index
            
            # Compute absolute valid bounds for this drag to prevent breaking limits/locks
            parent = self.master
            if hasattr(parent, 'table_panel'):
                P_min, P_max = self.grad_engine.compute_valid_passing_ranges(
                    parent.table_panel.retained,
                    parent.table_panel.locked_rows,
                    parent.table_panel.lower_limits,
                    parent.table_panel.upper_limits
                )
                table_idx = len(self.obtained) - 1 - index
                self._drag_min_passing = P_min[table_idx]
                self._drag_max_passing = P_max[table_idx]
            else:
                self._drag_min_passing = 0.0
                self._drag_max_passing = 100.0
                
            self._drag_start_y = event.ydata
            self._drag_start_value = float(self.obtained[index])
            self._update_entry_field()

    def _on_drag(self, event):
        if self.drag_index is not None:
            if event.ydata is None:
                return
            idx = self.drag_index
            
            # Raw coordinate
            y = event.ydata

            # Apply snap/precision logic
            if self.shift_held and self._drag_start_y is not None:
                # Precision mode: scale movement by 0.1
                delta = event.ydata - self._drag_start_y
                y = self._drag_start_value + delta * 0.1
            else:
                # Apply snap
                y = self._apply_snap(y)
            
            # Strictly clamp to physically valid mathematical limits
            if hasattr(self, '_drag_min_passing'):
                y = max(self._drag_min_passing, min(self._drag_max_passing, y))
            else:
                y = max(self.lower[idx], min(self.upper[idx], y))

            # Store the proposed y
            self.obtained[idx] = y

        # Enforce monotonicity in graph order (non-decreasing left→right)
        locked_graph = self._get_locked_graph_indices()
        self.obtained = self.grad_engine.enforce_monotonicity_graph_order(
            self.obtained, self.lower, self.upper, locked_graph
        )

        self._update_entry_field()

        # Update retained + table
        self._sync_back()

        # Fast blit redraw
        self._fast_update_curve()

    def _on_release(self, event):
        if self.drag_index is not None:
            # Do a final full redraw for clean visuals
            self._redraw_graph()
        self.drag_index = None
        self._drag_start_y = None
        self._drag_start_value = None

    def _on_resize(self, event):
        """Handle window resize."""
        # Matplotlib handles resize normally. We don't need to manually redraw
        # since we now capture the blitting background only on click.
        pass

    def _on_key_up(self, event):
        """Handle Up arrow key to increase selected point's passing %"""
        if self.selected_index is not None:
            locked_graph = self._get_locked_graph_indices()
            if self.selected_index in locked_graph:
                return  # Can't move locked points

            step = self.step_size * (0.1 if self.shift_held else 1.0)
            new_val = self.obtained[self.selected_index] + step
            new_val = self._apply_snap(new_val)
            new_val = max(self.lower[self.selected_index], min(self.upper[self.selected_index], new_val))
            self.obtained[self.selected_index] = new_val

            # Enforce monotonicity
            self.obtained = self.grad_engine.enforce_monotonicity_graph_order(
                self.obtained, self.lower, self.upper, locked_graph
            )

            self._update_entry_field()
            self._sync_back()
            self._redraw_graph()

    def _on_key_down(self, event):
        """Handle Down arrow key to decrease selected point's passing %"""
        if self.selected_index is not None:
            locked_graph = self._get_locked_graph_indices()
            if self.selected_index in locked_graph:
                return  # Can't move locked points

            step = self.step_size * (0.1 if self.shift_held else 1.0)
            new_val = self.obtained[self.selected_index] - step
            new_val = self._apply_snap(new_val)
            new_val = max(self.lower[self.selected_index], min(self.upper[self.selected_index], new_val))
            self.obtained[self.selected_index] = new_val

            # Enforce monotonicity
            self.obtained = self.grad_engine.enforce_monotonicity_graph_order(
                self.obtained, self.lower, self.upper, locked_graph
            )

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
            self.point_value_entry.insert(0, f"{value:.2f}% ({sieve_label}mm)")
            # Focus on entry field so keyboard events work
            self.point_value_entry.focus()

    def _on_entry_confirm(self, event):
        """Handle Enter key in the input field to set point value directly"""
        if self.selected_index is None:
            return
        
        locked_graph = self._get_locked_graph_indices()
        if self.selected_index in locked_graph:
            return  # Can't edit locked points
        
        try:
            # Parse the input (handle "XX.X% (mm)" format or just "XX.X")
            text = self.point_value_entry.get()
            value = float(text.split("%")[0].strip())
        except:
            return
        
        # Clamp to limits
        value = max(self.lower[self.selected_index], min(self.upper[self.selected_index], value))
        value = self._apply_snap(value)
        self.obtained[self.selected_index] = value
        
        # Enforce monotonicity
        self.obtained = self.grad_engine.enforce_monotonicity_graph_order(
            self.obtained, self.lower, self.upper, locked_graph
        )
        
        self._update_entry_field()
        self._sync_back()
        self._redraw_graph()

    def _on_entry_key_up(self, event):
        """Handle Up arrow key in entry field"""
        if self.selected_index is not None:
            locked_graph = self._get_locked_graph_indices()
            if self.selected_index in locked_graph:
                return "break"

            step = self.step_size * (0.1 if self.shift_held else 1.0)
            new_val = self.obtained[self.selected_index] + step
            new_val = self._apply_snap(new_val)
            new_val = max(self.lower[self.selected_index], min(self.upper[self.selected_index], new_val))
            self.obtained[self.selected_index] = new_val

            self.obtained = self.grad_engine.enforce_monotonicity_graph_order(
                self.obtained, self.lower, self.upper, locked_graph
            )

            self._update_entry_field()
            self._sync_back()
            self._redraw_graph()
        return "break"  # Prevent default behavior

    def _on_entry_key_down(self, event):
        """Handle Down arrow key in entry field"""
        if self.selected_index is not None:
            locked_graph = self._get_locked_graph_indices()
            if self.selected_index in locked_graph:
                return "break"

            step = self.step_size * (0.1 if self.shift_held else 1.0)
            new_val = self.obtained[self.selected_index] - step
            new_val = self._apply_snap(new_val)
            new_val = max(self.lower[self.selected_index], min(self.upper[self.selected_index], new_val))
            self.obtained[self.selected_index] = new_val

            self.obtained = self.grad_engine.enforce_monotonicity_graph_order(
                self.obtained, self.lower, self.upper, locked_graph
            )

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
        
        # Protect locked retained weights!
        # If user dragged a point, it creates a proposed passing curve. We must snap it to respect locks.
        final_passing, retained = self.grad_engine.sync_passing_with_locks(
            table_passing, 
            parent.table_panel.retained, 
            parent.table_panel.locked_rows, 
            parent.table_panel.lower_limits, 
            parent.table_panel.upper_limits
        )
        
        # The graph might have been forced to snap to satisfy the locked retained weights.
        self.obtained = np.array(list(reversed(final_passing)), dtype=float)

        # Update both passing and retained in table atomically
        parent.table_panel.passing = final_passing
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