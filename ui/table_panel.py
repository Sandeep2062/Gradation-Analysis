import customtkinter as ctk
from tkinter import ttk
from config.materials import materials
from core.fm_calculator import FMCalculator
from core.gradation_engine import GradationEngine

class TablePanel(ctk.CTkFrame):

    def __init__(self, parent, total_weight_manager):
        super().__init__(parent, fg_color="#1a1f2e", corner_radius=12)

        self.material_key = "fine"
        self.data = materials[self.material_key]

        self.fm_calc = FMCalculator()
        self.total_weight_manager = total_weight_manager
        self.grad_engine = GradationEngine(total_weight_manager)

        self.sieve_sizes = []
        self.lower_limits = []
        self.upper_limits = []
        self.passing = []
        self.retained = []

        self._build_ui()
        self._init_table_data()

    # ----------------------------------------------------
    # UI BUILD
    # ----------------------------------------------------

    def _build_ui(self):

        title = ctk.CTkLabel(self, text="📊 Gradation Table", font=("Segoe UI", 16, "bold"))
        title.pack(pady=(10, 5))

        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "Treeview",
            background="#252d3d",
            foreground="white",
            rowheight=35,
            fieldbackground="#252d3d",
            bordercolor="#3d4857",
            borderwidth=1,
            font=("Segoe UI", 11)
        )
        style.configure(
            "Treeview.Heading",
            background="#1a1f2e",
            foreground="white",
            borderwidth=1,
            font=("Segoe UI", 11, "bold")
        )
        style.map("Treeview", background=[("selected", "#0891b2")])
        style.map("Treeview.Heading", background=[("active", "#2d3748")])

        self.table = ttk.Treeview(
            self,
            columns=("sieve", "lower", "upper", "passing", "retained"),
            show="headings",
            height=8
        )

        self.table.heading("sieve", text="Sieve Size (mm)")
        self.table.heading("lower", text="Lower Limit (%)")
        self.table.heading("upper", text="Upper Limit (%)")
        self.table.heading("passing", text="% Passing")
        self.table.heading("retained", text="Weight Retained (g)")

        self.table.column("sieve", width=140, anchor="center")
        self.table.column("lower", width=140, anchor="center")
        self.table.column("upper", width=140, anchor="center")
        self.table.column("passing", width=140, anchor="center")
        self.table.column("retained", width=160, anchor="center")

        self.table.pack(fill="both", expand=True, padx=10, pady=10)

        self.table.bind("<Double-1>", self._begin_edit)

    # ----------------------------------------------------
    # TABLE DATA INIT
    # ----------------------------------------------------

    def _init_table_data(self):
        self.table.delete(*self.table.get_children())

        # Default empty startup
        for _ in range(7):
            self.table.insert("", "end", values=("", "", "", "", ""))

    def load_material(self, material_key):
        self.material_key = material_key
        self.data = materials[material_key]

        # Load sieve sizes and limits from config
        self.sieve_sizes = self.data["sieve_sizes"]
        self.lower_limits = self.data["lower_limits"]
        self.upper_limits = self.data["upper_limits"]
        
        # Initialize passing and retained with middle values between limits
        row_count = len(self.sieve_sizes)
        self.passing = [(self.lower_limits[i] + self.upper_limits[i]) / 2 for i in range(row_count)]
        
        # Calculate retained from passing values using gradation engine
        self.retained = self.grad_engine.passing_to_retained(self.passing)

        self._refresh_table()


    def _refresh_table(self):
        self.table.delete(*self.table.get_children())

        for i in range(len(self.sieve_sizes)):
            row = (
                self.sieve_sizes[i],
                f"{self.lower_limits[i]:.0f}",
                f"{self.upper_limits[i]:.0f}",
                f"{self.passing[i]:.1f}",
                f"{int(round(self.retained[i]))}"
            )
            self.table.insert("", "end", values=row)

    # ----------------------------------------------------
    # EDITING
    # ----------------------------------------------------

    def _begin_edit(self, event):
        region = self.table.identify("region", event.x, event.y)
        if region != "cell":
            return

        row_id = self.table.identify_row(event.y)
        col = self.table.identify_column(event.x)
        col_index = int(col.replace("#", "")) - 1

        if col_index == 0 or col_index == 1 or col_index == 2:
            return  # sieve, lower, upper are read-only

        bbox = self.table.bbox(row_id, col)
        if not bbox:
            return

        entry = ctk.CTkEntry(self, width=bbox[2], height=bbox[3])
        entry.place(x=bbox[0] + 10, y=bbox[1] + 65)

        old_value = self.table.item(row_id)["values"][col_index]
        entry.insert(0, old_value)

        entry.focus()

        entry.bind("<Return>", lambda e: self._finish_edit(entry, row_id, col_index))
        entry.bind("<FocusOut>", lambda e: self._finish_edit(entry, row_id, col_index))

    def _finish_edit(self, entry, row_id, col_index):
        new_val = entry.get().strip()
        entry.destroy()

        try:
            new_val = float(new_val)
        except:
            return

        row_index = self.table.index(row_id)

        # update data arrays
        if col_index == 3:
            self.passing[row_index] = new_val
        elif col_index == 4:
            self.retained[row_index] = new_val

        self._refresh_table()

        # sync graph + FM
        parent = self.master
        parent.graph_panel.update_curve(self.passing)
        parent.input_panel.update_fm(self.retained)

    # ----------------------------------------------------
    # PUBLIC API
    # ----------------------------------------------------

    def get_limits(self):
        return (self.lower_limits, self.upper_limits)

    def get_sieve_sizes(self):
        return self.sieve_sizes

    def update_passing(self, new_curve):
        self.passing = new_curve
        self._refresh_table()

    def update_retained(self, new_retained):
        self.retained = new_retained
        self._refresh_table()
