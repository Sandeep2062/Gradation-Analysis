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

        self._active_entry = None  # Track active edit entry

        self._build_ui()
        self._init_table_data()

    # ----------------------------------------------------
    # UI BUILD
    # ----------------------------------------------------

    def _build_ui(self):
        # Header with title + hint
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(10, 5))

        title = ctk.CTkLabel(header, text="📊 Gradation Table", font=("Segoe UI", 16, "bold"))
        title.pack(side="left")

        self.edit_hint = ctk.CTkLabel(
            header,
            text="Double-click to edit  % Passing  or  Weight Retained",
            font=("Segoe UI", 10, "italic"),
            text_color="#64748b"
        )
        self.edit_hint.pack(side="right")

        # Treeview styling
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "Gradation.Treeview",
            background="#252d3d",
            foreground="white",
            rowheight=34,
            fieldbackground="#252d3d",
            bordercolor="#1e293b",
            borderwidth=0,
            font=("Segoe UI", 11)
        )
        style.configure(
            "Gradation.Treeview.Heading",
            background="#1e293b",
            foreground="#e2e8f0",
            borderwidth=0,
            relief="flat",
            font=("Segoe UI", 11, "bold")
        )
        style.map("Gradation.Treeview", background=[("selected", "#0e7490")])
        style.map("Gradation.Treeview.Heading", background=[("active", "#334155")])

        # Table container
        self.table_frame = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=8)
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 5))

        self.table = ttk.Treeview(
            self.table_frame,
            columns=("sieve", "lower", "upper", "passing", "retained"),
            show="headings",
            height=8,
            style="Gradation.Treeview"
        )

        self.table.heading("sieve", text="Sieve Size (mm)")
        self.table.heading("lower", text="Lower Limit (%)")
        self.table.heading("upper", text="Upper Limit (%)")
        self.table.heading("passing", text="% Passing  ✏️")
        self.table.heading("retained", text="Wt. Retained (g)  ✏️")

        self.table.column("sieve", width=130, anchor="center", minwidth=90)
        self.table.column("lower", width=130, anchor="center", minwidth=90)
        self.table.column("upper", width=130, anchor="center", minwidth=90)
        self.table.column("passing", width=130, anchor="center", minwidth=90)
        self.table.column("retained", width=170, anchor="center", minwidth=110)

        # Alternating row colors
        self.table.tag_configure("evenrow", background="#252d3d")
        self.table.tag_configure("oddrow", background="#2a3347")
        self.table.tag_configure("panrow", background="#1e3a5f")

        self.table.pack(fill="both", expand=True)
        self.table.bind("<Double-1>", self._begin_edit)

        # Summary bar showing total retained weight
        summary = ctk.CTkFrame(self, fg_color="#252d3d", corner_radius=8, height=38)
        summary.pack(fill="x", padx=10, pady=(0, 10))

        self.total_retained_label = ctk.CTkLabel(
            summary, text="∑ Total Retained: 0 g",
            font=("Segoe UI", 12, "bold"), text_color="#0891b2"
        )
        self.total_retained_label.pack(side="left", padx=15, pady=8)

        self.status_label = ctk.CTkLabel(
            summary, text="",
            font=("Segoe UI", 11), text_color="#94a3b8"
        )
        self.status_label.pack(side="right", padx=15, pady=8)

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

        # Keep original order for calculations (largest to smallest/Pan)
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

        total_retained = 0.0
        for i in range(len(self.sieve_sizes)):
            retained_val = self.retained[i]
            total_retained += retained_val

            # Alternating row colors
            if self.sieve_sizes[i] == "Pan":
                tag = "panrow"
            elif i % 2 == 0:
                tag = "evenrow"
            else:
                tag = "oddrow"

            row = (
                self.sieve_sizes[i],
                f"{self.lower_limits[i]:.0f}",
                f"{self.upper_limits[i]:.0f}",
                f"{self.passing[i]:.1f}",
                f"{int(round(retained_val))}"
            )
            self.table.insert("", "end", values=row, tags=(tag,))

        # Update summary bar
        target = self.total_weight_manager.get_total_weight()
        diff = abs(total_retained - target)
        self.total_retained_label.configure(text=f"∑ Total Retained: {total_retained:.0f} g")

        if diff < 1:
            self.status_label.configure(text="✓ Balanced", text_color="#22c55e")
        else:
            self.status_label.configure(
                text=f"⚠ Off by {diff:.0f}g (target: {target:.0f}g)",
                text_color="#f59e0b"
            )

    # ----------------------------------------------------
    # EDITING
    # ----------------------------------------------------

    def _begin_edit(self, event):
        # Destroy any existing edit entry
        if self._active_entry:
            try:
                self._active_entry.destroy()
            except:
                pass
            self._active_entry = None

        region = self.table.identify("region", event.x, event.y)
        if region != "cell":
            return

        row_id = self.table.identify_row(event.y)
        col = self.table.identify_column(event.x)
        col_index = int(col.replace("#", "")) - 1

        # Only passing (3) and retained (4) are editable
        if col_index not in (3, 4):
            return

        bbox = self.table.bbox(row_id, col)
        if not bbox:
            return

        # Calculate proper position using absolute coordinates
        abs_x = self.table.winfo_rootx() + bbox[0]
        abs_y = self.table.winfo_rooty() + bbox[1]
        self_x = abs_x - self.winfo_rootx()
        self_y = abs_y - self.winfo_rooty()

        entry = ctk.CTkEntry(
            self,
            width=bbox[2],
            height=bbox[3],
            fg_color="#0f172a",
            border_color="#0891b2",
            border_width=2,
            text_color="#22d3ee",
            font=("Segoe UI", 12, "bold"),
            justify="center",
            corner_radius=0
        )
        entry.place(x=self_x, y=self_y)
        self._active_entry = entry

        old_value = self.table.item(row_id)["values"][col_index]
        entry.insert(0, str(old_value))
        entry.select_range(0, "end")
        entry.focus()

        def on_escape(e):
            entry.destroy()
            self._active_entry = None

        entry.bind("<Return>", lambda e: self._finish_edit(entry, row_id, col_index))
        entry.bind("<FocusOut>", lambda e: self._finish_edit(entry, row_id, col_index))
        entry.bind("<Escape>", on_escape)

    def _finish_edit(self, entry, row_id, col_index):
        new_val = entry.get().strip()
        entry.destroy()
        self._active_entry = None

        try:
            new_val = float(new_val)
        except:
            return

        row_index = self.table.index(row_id)

        if col_index == 3:  # Passing % edited
            # Clamp passing % to limits
            new_val = max(self.lower_limits[row_index], min(self.upper_limits[row_index], new_val))
            self.passing[row_index] = new_val
            # Recalculate retained from passing
            self.retained = self.grad_engine.passing_to_retained(self.passing)

        elif col_index == 4:  # Weight retained edited — AUTO-ADJUST others
            new_val = max(0, new_val)
            total_weight = self.total_weight_manager.get_total_weight()
            new_val = min(new_val, total_weight)  # Cannot exceed total

            # Proportional adjustment: other retained values scale to keep total = total_weight
            other_indices = [j for j in range(len(self.retained)) if j != row_index]
            other_total = sum(self.retained[j] for j in other_indices)

            self.retained[row_index] = new_val
            remaining = total_weight - new_val

            if other_total > 0 and remaining >= 0:
                scale = remaining / other_total
                for j in other_indices:
                    self.retained[j] = max(0, self.retained[j] * scale)
            elif len(other_indices) > 0 and remaining > 0:
                # All others are zero — distribute equally
                per_sieve = remaining / len(other_indices)
                for j in other_indices:
                    self.retained[j] = per_sieve

            # Recalculate passing from the adjusted retained
            self.passing = self._retained_to_passing(self.retained)

        self._refresh_table()

        # Sync graph + FM
        parent = self.master
        parent.graph_panel.update_curve(self.passing)
        parent.input_panel.update_fm(self.retained)

    def _retained_to_passing(self, retained_weights):
        """
        Convert retained weights back to passing percentages.
        This is the inverse of passing_to_retained.
        """
        import numpy as np
        retained = np.array(retained_weights, dtype=float)
        
        # Get total weight
        total_wt = self.total_weight_manager.get_total_weight()
        
        if total_wt <= 0:
            return [50.0] * len(retained)
        
        # Convert retained weights to fractions
        retained_frac = retained / total_wt
        retained_frac = np.clip(retained_frac, 0, None)
        
        # Convert retained fractions to passing fractions
        passing_frac = np.zeros_like(retained_frac)
        passing_frac[0] = 1 - retained_frac[0]
        
        for i in range(1, len(retained_frac)):
            passing_frac[i] = passing_frac[i-1] - retained_frac[i]
        
        # Clip to valid range [0, 1] and convert to percentages [0, 100]
        passing_frac = np.clip(passing_frac, 0, 1)
        passing = passing_frac * 100
        
        return passing.tolist()

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
