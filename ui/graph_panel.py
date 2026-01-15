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

        self.grad_engine = GradationEngine()

        self.sieve_sizes = []
        self.lower = []
        self.upper = []
        self.obtained = []

        self.drag_index = None

        self._build_graph()

    # ----------------------------------------------------
    # BUILD GRAPH UI
    # ----------------------------------------------------

    def _build_graph(self):
        self.figure, self.ax = plt.subplots(figsize=(6,4), dpi=90)
        self.figure.patch.set_facecolor('#0f172a')
        self.ax.set_facecolor('#0f172a')

        self.ax.tick_params(colors="white")
        self.ax.spines["bottom"].set_color("white")
        self.ax.spines["left"].set_color("white")
        self.ax.spines["top"].set_color("#0f172a")
        self.ax.spines["right"].set_color("#0f172a")

        self.ax.set_xlabel("Sieve Size", color="white")
        self.ax.set_ylabel("% Passing", color="white")

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

        # basic placeholders
        n = len(self.data["sieve_range"])

        self.sieve_sizes = np.linspace(1, n, n)
        self.lower = np.linspace(50, 70, n)
        self.upper = np.linspace(80, 95, n)
        self.obtained = np.linspace(65, 85, n)

        self._redraw_graph()

    # ----------------------------------------------------
    # DRAW GRAPH
    # ----------------------------------------------------

    def _redraw_graph(self):
        """Redraws the entire graph with current data"""
        self.ax.clear()
        self.ax.set_facecolor('#0f172a')
        self.ax.tick_params(colors="white")
        self.ax.spines["bottom"].set_color("white")
        self.ax.spines["left"].set_color("white")
        self.ax.spines["top"].set_color("#0f172a")
        self.ax.spines["right"].set_color("#0f172a")

        # lower/upper limit curves
        self.ax.plot(self.sieve_sizes, self.lower, color="#94a3b8", linewidth=1.2, linestyle="--", alpha=0.7, label="Lower Limit")
        self.ax.plot(self.sieve_sizes, self.upper, color="#94a3b8", linewidth=1.2, linestyle="--", alpha=0.7, label="Upper Limit")

        # obtained curve (cyan)
        self.ax.plot(self.sieve_sizes, self.obtained, color="#06b6d4", linewidth=2.5, label="Obtained")

        # draggable points
        self.ax.scatter(self.sieve_sizes, self.obtained, color="#06b6d4", s=50, edgecolor="white", zorder=5)

        self.ax.set_xlabel("Sieve Index", color="white")
        self.ax.set_ylabel("% Passing", color="white")
        self.ax.legend(facecolor="#1e293b", edgecolor="white", labelcolor="white")

        self.canvas.draw()

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

        self._redraw_graph()

    def _on_release(self, event):
        self.drag_index = None

    # ----------------------------------------------------
    # SYNC TO TABLE + FM
    # ----------------------------------------------------

    def _sync_back(self):
        parent = self.master

        # update table
        parent.table_panel.update_passing(list(self.obtained))

        # calculate retained based on passing
        retained = self.grad_engine.passing_to_retained(self.obtained)

        # update retained in table
        parent.table_panel.update_retained(retained)

        # update FM
        parent.input_panel.update_fm(retained)

    # ----------------------------------------------------

    def update_curve(self, new_curve):
        self.obtained = np.array(new_curve)
        self._sync_back()
        self._redraw_graph()