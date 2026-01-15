import customtkinter as ctk
from core.total_weight import TotalWeightManager
from core.random_generator import RandomCurveGenerator
from core.fm_calculator import FMCalculator
from config.materials import materials

class InputPanel(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="#1a1f2e", corner_radius=15)

        self.material_key = "fine"
        self.data = materials[self.material_key]

        self.total_weight_manager = TotalWeightManager()
        self.random_gen = RandomCurveGenerator()
        self.fm_calc = FMCalculator()

        self._build_ui()

    def _build_ui(self):
        title = ctk.CTkLabel(
            self,
            text="⚙️ Input Settings",
            font=("Segoe UI", 18, "bold"),
            text_color="white"
        )
        title.pack(pady=(15, 10))

        # TOTAL WEIGHT INPUT
        self.total_label = ctk.CTkLabel(self, text="Total Weight (gm):", font=("Segoe UI", 13), text_color="#cbd5e1")
        self.total_label.pack(pady=(15, 3))

        self.total_entry = ctk.CTkEntry(self, width=140, corner_radius=8, fg_color="#252d3d", border_color="#0891b2", border_width=2, text_color="white")
        self.total_entry.insert(0, "5000")
        self.total_entry.pack(pady=8)

        self.total_entry.bind("<KeyRelease>", lambda e: self._on_change_total_weight())

        # RANDOM BUTTON
        self.random_btn = ctk.CTkButton(
            self,
            text="🎲 Generate Random Curve",
            fg_color="#0891b2",
            hover_color="#06b6d4",
            corner_radius=10,
            text_color="white",
            font=("Segoe UI", 12, "bold"),
            command=self._generate_random
        )
        self.random_btn.pack(pady=(25, 15))

        # FM OUTPUT
        self.fm_label = ctk.CTkLabel(
            self,
            text="Fineness Modulus: -",
            font=("Segoe UI", 14),
            text_color="#cbd5e1"
        )
        self.fm_label.pack(pady=(10, 20))

    # -------------------- CORE LOGIC -------------------- #

    def load_material(self, material_key):
        self.material_key = material_key
        self.data = materials[material_key]

    def update_fm(self, retained_list):
        fm_value = self.fm_calc.calculate_fm(retained_list)
        self.fm_label.configure(text=f"Fineness Modulus: {fm_value:.3f}")

    def _on_change_total_weight(self):
        try:
            weight = float(self.total_entry.get())
        except:
            return

        self.total_weight_manager.set_total_weight(weight)

    def _generate_random(self):
        parent = self.master

        # request limits from table panel
        lower, upper = parent.table_panel.get_limits()
        sieve_sizes = parent.table_panel.get_sieve_sizes()

        random_curve = self.random_gen.generate(sieve_sizes, lower, upper)

        parent.graph_panel.update_curve(random_curve)
        parent.table_panel.update_passing(random_curve)
