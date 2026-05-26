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
        self.locked_rows = set()  # Track which row indices are locked

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
            text="Double-click to edit  % Passing  or  Weight Retained  |  🔒 = value protected",
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
            columns=("sieve", "lower", "upper", "passing", "retained", "lock"),
            show="headings",
            height=8,
            style="Gradation.Treeview"
        )

        self.table.heading("sieve", text="Sieve Size (mm)")
        self.table.heading("lower", text="Lower Limit (%)")
        self.table.heading("upper", text="Upper Limit (%)")
        self.table.heading("passing", text="% Passing  ✏️")
        self.table.heading("retained", text="Wt. Retained (g)  ✏️")
        self.table.heading("lock", text="Lock")

        self.table.column("sieve", width=120, anchor="center", minwidth=90)
        self.table.column("lower", width=120, anchor="center", minwidth=90)
        self.table.column("upper", width=120, anchor="center", minwidth=90)
        self.table.column("passing", width=120, anchor="center", minwidth=90)
        self.table.column("retained", width=160, anchor="center", minwidth=110)
        self.table.column("lock", width=60, anchor="center", minwidth=50)

        # Alternating row colors
        self.table.tag_configure("evenrow", background="#252d3d")
        self.table.tag_configure("oddrow", background="#2a3347")
        self.table.tag_configure("panrow", background="#1e3a5f")
        self.table.tag_configure("locked_evenrow", background="#2d2520")
        self.table.tag_configure("locked_oddrow", background="#332a22")
        self.table.tag_configure("locked_panrow", background="#2a3020")

        self.table.pack(fill="both", expand=True)
        self.table.bind("<Double-1>", self._begin_edit)
        self.table.bind("<ButtonRelease-1>", self._on_click)

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
            self.table.insert("", "end", values=("", "", "", "", "", ""))

    def load_material(self, material_key):
        self.material_key = material_key
        self.data = materials[material_key]

        # Keep original order for calculations (largest to smallest/Pan)
        self.sieve_sizes = self.data["sieve_sizes"]
        self.lower_limits = self.data["lower_limits"]
        self.upper_limits = self.data["upper_limits"]
        self.locked_rows = set()  # Reset locks on material change
        
        # Initialize passing and retained with middle values between limits
        row_count = len(self.sieve_sizes)
        self.passing = [(self.lower_limits[i] + self.upper_limits[i]) / 2 for i in range(row_count)]
        
        # Enforce monotonicity on initial values
        self.passing = self.grad_engine.enforce_monotonicity_table_order(
            self.passing, self.lower_limits, self.upper_limits
        )
        
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

            lock_icon = "[ Locked ]" if i in self.locked_rows else "[   ]"

            # Use locked tag variants for locked rows
            if i in self.locked_rows:
                if self.sieve_sizes[i] == "Pan":
                    tag = "locked_panrow"
                elif i % 2 == 0:
                    tag = "locked_evenrow"
                else:
                    tag = "locked_oddrow"

            row = (
                self.sieve_sizes[i],
                f"{self.lower_limits[i]:.0f}",
                f"{self.upper_limits[i]:.0f}",
                f"{self.passing[i]:.2f}",
                f"{retained_val:.1f}",
                lock_icon
            )
            self.table.insert("", "end", values=row, tags=(tag,))

        # Update summary bar
        target = self.total_weight_manager.get_total_weight()
        diff = abs(total_retained - target)
        self.total_retained_label.configure(text=f"∑ Total Retained: {total_retained:.1f} g")

        if diff < 1:
            self.status_label.configure(text="✓ Balanced", text_color="#22c55e")
        else:
            self.status_label.configure(
                text=f"⚠ Off by {diff:.1f}g (target: {target:.0f}g)",
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

        # Don't allow editing locked rows
        row_index = self.table.index(row_id)
        if row_index in self.locked_rows:
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
            self._handle_passing_edit(row_index, new_val)

        elif col_index == 4:  # Weight retained edited
            self._handle_retained_edit(row_index, new_val)

        self._refresh_table()

        # Sync graph + FM
        parent = self.master
        parent.graph_panel.update_curve(self.passing)
        parent.input_panel.update_fm(self.retained)

    def _handle_passing_edit(self, row_index, new_val):
        """
        Handle editing of % Passing value.
        - Clamp to [lower_limit, upper_limit]
        - Sync to ensure we NEVER change locked retained weights
        """
        # Clamp to limits
        new_val = max(self.lower_limits[row_index], min(self.upper_limits[row_index], new_val))
        self.passing[row_index] = new_val

        # Sync using the engine to protect locked retained values
        self.passing, self.retained = self.grad_engine.sync_passing_with_locks(
            self.passing, 
            self.retained, 
            self.locked_rows, 
            self.lower_limits, 
            self.upper_limits
        )

    def _handle_retained_edit(self, row_index, new_val):
        """
        Handle editing of Weight Retained value.
        - Auto-clamp to physically valid [min_allowed, max_allowed] required by envelope.
        - Locked rows are NEVER changed
        - Redistribute remaining weight among unlocked rows proportionally
        - Recalculate passing from the adjusted retained values
        """
        # Calculate the absolute mathematical bounds for this row to stay inside limits
        min_val, max_val = self.grad_engine.compute_valid_retained_range(
            row_index, self.retained, self.locked_rows,
            self.lower_limits, self.upper_limits
        )

        # Auto-clamp user input so it NEVER breaks limits
        new_val = max(min_val, min(new_val, max_val))

        # Use engine to redistribute among unlocked rows
        self.retained = self.grad_engine.adjust_retained_with_locks(
            self.retained, row_index, new_val, self.locked_rows
        )

        # Recalculate passing from the adjusted retained
        # Since all retained values are >= 0, passing is guaranteed to be monotonic.
        self.passing = self.grad_engine.retained_to_passing(self.retained)

    # ----------------------------------------------------
    # PUBLIC API
    # ----------------------------------------------------

    def get_limits(self):
        return (self.lower_limits, self.upper_limits)

    def get_sieve_sizes(self):
        return self.sieve_sizes

    def update_passing(self, new_curve):
        self.passing = list(new_curve)
        self._refresh_table()

    def update_retained(self, new_retained):
        self.retained = list(new_retained)
        self._refresh_table()

    # ----------------------------------------------------
    # LOCK TOGGLE
    # ----------------------------------------------------

    def _on_click(self, event):
        """Handle single click — toggle lock if Lock column is clicked."""
        region = self.table.identify("region", event.x, event.y)
        if region != "cell":
            return

        col = self.table.identify_column(event.x)
        col_index = int(col.replace("#", "")) - 1

        # Lock column is index 5
        if col_index != 5:
            return

        row_id = self.table.identify_row(event.y)
        if not row_id:
            return

        row_index = self.table.index(row_id)

        if row_index in self.locked_rows:
            self.locked_rows.discard(row_index)
        else:
            self.locked_rows.add(row_index)

        self._refresh_table()
        
        # Also update graph to show lock status on points
        parent = self.master
        if hasattr(parent, 'graph_panel'):
            parent.graph_panel._redraw_graph()
