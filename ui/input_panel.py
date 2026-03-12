import customtkinter as ctk
from core.random_generator import RandomCurveGenerator
from core.fm_calculator import FMCalculator
from config.materials import materials
import numpy as np

class InputPanel(ctk.CTkFrame):

    def __init__(self, parent, total_weight_manager):
        super().__init__(parent, fg_color="#1a1f2e", corner_radius=15, width=220)

        self.material_key = "fine"
        self.data = materials[self.material_key]

        self.total_weight_manager = total_weight_manager
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

        # Separator
        sep = ctk.CTkFrame(self, fg_color="#334155", height=1)
        sep.pack(fill="x", padx=15, pady=(0, 10))

        # TOTAL WEIGHT INPUT
        self.total_label = ctk.CTkLabel(self, text="Total Weight (gm):", font=("Segoe UI", 13), text_color="#cbd5e1")
        self.total_label.pack(pady=(10, 3))

        self.total_entry = ctk.CTkEntry(
            self, width=160, height=38, corner_radius=8,
            fg_color="#252d3d", border_color="#0891b2", border_width=2,
            text_color="white", font=("Segoe UI", 13), justify="center"
        )
        self.total_entry.insert(0, "5000")
        self.total_entry.pack(pady=8)

        self.total_entry.bind("<KeyRelease>", lambda e: self._on_change_total_weight())
        
        # Set initial total weight
        self._on_change_total_weight()

        # Separator
        sep2 = ctk.CTkFrame(self, fg_color="#334155", height=1)
        sep2.pack(fill="x", padx=15, pady=(15, 10))

        # RANDOM BUTTON
        self.random_btn = ctk.CTkButton(
            self,
            text="🎲  Generate Random Curve",
            fg_color="#0891b2",
            hover_color="#06b6d4",
            corner_radius=10,
            height=42,
            text_color="white",
            font=("Segoe UI", 13, "bold"),
            command=self._generate_random
        )
        self.random_btn.pack(pady=(15, 15), padx=15, fill="x")

        # Separator
        sep3 = ctk.CTkFrame(self, fg_color="#334155", height=1)
        sep3.pack(fill="x", padx=15, pady=(5, 10))

        # FM OUTPUT
        self.fm_label = ctk.CTkLabel(
            self,
            text="Fineness Modulus: —",
            font=("Segoe UI", 15, "bold"),
            text_color="#0891b2"
        )
        self.fm_label.pack(pady=(10, 3))

        # FM Zone label (for sand materials)
        self.fm_zone_label = ctk.CTkLabel(
            self,
            text="",
            font=("Segoe UI", 12),
            text_color="#94a3b8"
        )
        self.fm_zone_label.pack(pady=(0, 20))

    # -------------------- CORE LOGIC -------------------- #

    def load_material(self, material_key):
        self.material_key = material_key
        self.data = materials[material_key]

    def update_fm(self, retained_list):
        fm_value = self.fm_calc.calculate_fm(retained_list)
        self.fm_label.configure(text=f"Fineness Modulus: {fm_value:.3f}")

        # Show zone classification for sand materials
        if self.material_key in ("fine", "finesand"):
            if fm_value < 2.2:
                zone = "Zone IV (Very Fine)"
                color = "#f59e0b"
            elif fm_value < 2.6:
                zone = "Zone III (Fine)"
                color = "#22c55e"
            elif fm_value < 2.9:
                zone = "Zone II (Medium) ✓"
                color = "#22c55e"
            elif fm_value < 3.2:
                zone = "Zone I (Coarse)"
                color = "#f59e0b"
            else:
                zone = "Zone I (Coarse)"
                color = "#f59e0b"
            self.fm_zone_label.configure(text=zone, text_color=color)
        else:
            self.fm_zone_label.configure(text="")

    def _on_change_total_weight(self):
        try:
            weight = float(self.total_entry.get())
        except:
            return

        self.total_weight_manager.set_total_weight(weight)
        
        # Trigger table update with recalculated retained values
        parent = self.master
        if hasattr(parent, 'table_panel'):
            # Recalculate retained values based on new total weight
            passing = parent.table_panel.passing
            retained = parent.table_panel.grad_engine.passing_to_retained(passing)
            parent.table_panel.update_retained(retained)
            # Update FM display
            self.update_fm(retained)

    def _generate_random(self):
        parent = self.master

        # Get limits from table panel (original order: largest to smallest)
        lower, upper = parent.table_panel.get_limits()
        sieve_sizes = parent.table_panel.get_sieve_sizes()

        # Generate random curve in table order (largest to smallest)
        random_curve = self.random_gen.generate(sieve_sizes, lower, upper)

        # Update table with new passing curve
        parent.table_panel.update_passing(random_curve)
        
        # Update graph (it will reverse internally for display)
        parent.graph_panel.update_curve(random_curve)
        
        # Recalculate retained and update FM
        retained = parent.table_panel.grad_engine.passing_to_retained(random_curve)
        parent.table_panel.update_retained(retained)
        self.update_fm(retained)

