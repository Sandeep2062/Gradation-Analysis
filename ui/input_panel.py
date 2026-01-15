import customtkinter as ctk
from core.total_weight import TotalWeightManager
from core.random_generator import RandomCurveGenerator
from core.fm_calculator import FMCalculator
from config.materials import materials

class InputPanel(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="#0f172a", corner_radius=15)

        self.material_key = "fine"
        self.data = materials[self.material_key]

        self.total_weight_manager = TotalWeightManager()
        self.random_gen = RandomCurveGenerator()
        self.fm_calc = FMCalculator()

        self._build_ui()

    def _build_ui(self):
        title = ctk.CTkLabel(
            self,
            text="Input Settings",
            font=("Segoe UI", 18, "bold")
        )
        title.pack(pady=(10, 5))

        # TOTAL WEIGHT INPUT
        self.total_label = ctk.CTkLabel(self, text="Total Weight (gm):", font=("Segoe UI", 14))
        self.total_label.pack(pady=(10, 0))

        self.total_entry = ctk.CTkEntry(self, width=140, corner_radius=8)
        self.total_entry.insert(0, "2000")
        self.total_entry.pack(pady=5)

        self.total_entry.bind("<KeyRelease>", lambda e: self._on_change_total_weight())

        # RANDOM BUTTON
        self.random_btn = ctk.CTkButton(
            self,
            text="Generate Random Curve",
            fg_color="#0891b2",
            hover_color="#0ea5e9",
            corner_radius=12,
            command=self._generate_random
        )
        self.random_btn.pack(pady=(20, 10))

        # FM OUTPUT
        self.fm_label = ctk.CTkLabel(
            self,
            text="Fineness Modulus: -",
            font=("Segoe UI", 15)
        )
        self.fm_label.pack(pady=(15, 5))

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
