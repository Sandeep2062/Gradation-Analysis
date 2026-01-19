import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
from config.materials import materials
from core.constraints import clamp_curve
from core.gradation_engine import GradationEngine

class GraphPanel(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="#1a1f2e", corner_radius=15)

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

        self._build_graph()

    # ----------------------------------------------------
    # BUILD GRAPH UI
    # ----------------------------------------------------

    def _build_graph(self):
        self.figure, self.ax = plt.subplots(figsize=(7,5), dpi=100)
        self.figure.patch.set_facecolor('#1a1f2e')
        self.ax.set_facecolor('#1a1f2e')

        self.ax.tick_params(colors="#b0bac9")
        self.ax.spines["bottom"].set_color("#3d4857")
        self.ax.spines["left"].set_color("#3d4857")
        self.ax.spines["top"].set_color("#1a1f2e")
        self.ax.spines["right"].set_color("#1a1f2e")

        self.ax.set_xlabel("Sieve Size", color="#b0bac9")
        self.ax.set_ylabel("% Passing", color="#b0bac9")

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas.mpl_connect("button_press_event", self._on_click)
        self.canvas.mpl_connect("motion_notify_event", self._on_drag)
        self.canvas.mpl_connect("button_release_event", self._on_release)

    # ----------------------------------------------------
    # LOAD MATERIAL LIMITS + SETUP
    # ----------------------------------------------------

    def load_material(self, material_key):
        self.material_key = material_key
        self.data = materials[material_key]

        # Load sieve data from config in ORIGINAL order (largest to smallest) for right-to-left display
        sieve_labels = self.data["sieve_sizes"]
        lower_limits = np.array(self.data["lower_limits"], dtype=float)
        upper_limits = np.array(self.data["upper_limits"], dtype=float)
        
        n = len(sieve_labels)
        self.sieve_sizes = np.arange(n)  # 0, 1, 2, ... for x-axis positions
        self.sieve_labels = sieve_labels  # Store labels for display (right to left: large to small)
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
        self.ax.set_facecolor('#1a1f2e')
        self.ax.tick_params(colors="#b0bac9", labelsize=10)
        self.ax.spines["bottom"].set_color("#3d4857")
        self.ax.spines["left"].set_color("#3d4857")
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        
        # Add grid for better readability
        self.ax.grid(True, alpha=0.2, color="#3d4857", linestyle="--", linewidth=0.5)

        # lower/upper limit curves
        self.ax.plot(self.sieve_sizes, self.lower, color="#94a3b8", linewidth=2, linestyle="--", alpha=0.8, label="Lower Limit")
        self.ax.plot(self.sieve_sizes, self.upper, color="#94a3b8", linewidth=2, linestyle="--", alpha=0.8, label="Upper Limit")

        # Shade the grading zone
        self.ax.fill_between(self.sieve_sizes, self.lower, self.upper, alpha=0.1, color="#0891b2")

        # obtained curve (cyan)
        self.ax.plot(self.sieve_sizes, self.obtained, color="#06b6d4", linewidth=3, label="Obtained", zorder=3)

        # draggable points - larger for better visibility
        self.ax.scatter(self.sieve_sizes, self.obtained, color="#06b6d4", s=100, edgecolor="white", zorder=5, linewidth=2)

        # Set x-axis with sieve size labels - BIGGER
        self.ax.set_xticks(self.sieve_sizes)
        self.ax.set_xticklabels([str(x) if isinstance(x, str) else f"{x:.2f}" for x in self.sieve_labels], rotation=45, ha='right', fontsize=11, fontweight='bold')
        self.ax.set_xlabel("Sieve Size (mm)", color="#b0bac9", fontsize=12, fontweight='bold')
        self.ax.set_ylabel("% Passing", color="#b0bac9", fontsize=12, fontweight='bold')
        self.ax.legend(facecolor="#252d3d", edgecolor="#3d4857", labelcolor="#b0bac9", loc='best', framealpha=0.95)
        self.ax.set_ylim(-5, 110)
        self.figure.tight_layout()

        self.canvas.draw()

    def _fast_update_curve(self):
        """Fast update of curve during dragging - only update line and scatter without full redraw"""
        # Find and update the obtained curve line (last plotted line, or search by color)
        lines = self.ax.get_lines()
        scatter_artists = self.ax.collections
        
        # Update the obtained curve line (usually the cyan/last data line)
        for line in lines:
            if line.get_color() == '#06b6d4':  # cyan color for obtained curve
                line.set_data(self.sieve_sizes, self.obtained)
                break
        
        # Update scatter points
        for scatter in scatter_artists:
            if hasattr(scatter, 'get_facecolor') and len(scatter.get_facecolor()) > 0:
                if scatter.get_facecolor()[0][2] > 0.8:  # Check if it's the cyan scatter
                    scatter.set_offsets(np.c_[self.sieve_sizes, self.obtained])
                    break
        
        # Quick redraw without layout recalculation
        self.canvas.draw_idle()

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

    def _on_drag(self, event):
        if self.drag_index is None:
            return
        if event.inaxes != self.ax:
            return

        # clamp inside limits
        y = event.ydata
        y = max(self.lower[self.drag_index], min(self.upper[self.drag_index], y))

        self.obtained[self.drag_index] = y

        # Update retained + table
        self._sync_back()

        # Fast redraw - only update the curve line and points without full layout recalculation
        self._fast_update_curve()

    def _on_release(self, event):
        self.drag_index = None

    # ----------------------------------------------------
    # SYNC TO TABLE + FM
    # ----------------------------------------------------

    def _sync_back(self):
        parent = self.master

        # obtained curve is already in table order (largest to smallest, same as table)
        table_passing = list(self.obtained)
        
        # update table
        parent.table_panel.update_passing(table_passing)

        # calculate retained based on passing in original order
        retained = self.grad_engine.passing_to_retained(table_passing)

        # update retained in table
        parent.table_panel.update_retained(retained)

        # update FM
        parent.input_panel.update_fm(retained)

    # ----------------------------------------------------

    def update_curve(self, new_curve):
        """Update curve from table edits"""
        # new_curve is in table order (largest to smallest) which is also the graph order now
        self.obtained = np.array(new_curve, dtype=float)
        self._redraw_graph()