import customtkinter as ctk

class TopTabs(ctk.CTkFrame):

    def __init__(self, parent, callback):
        super().__init__(parent, fg_color="#1a1f2e")

        self.callback = callback
        self.materials = {
            "fine": "Fine Aggregate",
            "coarse1": "Coarse Aggregate 1",
            "coarse2": "Coarse Aggregate 2",
            "subbase": "Sub-Base",
            "crm": "CRM for Base"
        }

        self.current = "fine"
        self.buttons = {}

        self._build_tabs()

    def _build_tabs(self):
        # Dynamic grid configuration for 5 tabs
        for i in range(5):
            self.grid_columnconfigure(i, weight=1)

        tabs_data = [
            ("fine", "⚙️ Fine Aggregate"),
            ("coarse1", "🏔️ Coarse Aggregate 1"),
            ("coarse2", "🏔️ Coarse Aggregate 2"),
            ("subbase", "🏗️ Sub-Base"),
            ("crm", "🔨 CRM for Base")
        ]

        for idx, (key, label) in enumerate(tabs_data):
            btn = ctk.CTkButton(
                self,
                text=label,
                corner_radius=12,
                fg_color="#2d3748" if key != "fine" else "#0891b2",
                border_width=0 if key == "fine" else 2,
                border_color="#0891b2" if key != "fine" else None,
                text_color="white",
                font=("Segoe UI", 13, "bold"),
                hover_color="#0ea5e9" if key == "fine" else "#3d4857",
                command=lambda k=key: self._switch(k)
            )
            btn.grid(row=0, column=idx, padx=6, pady=10, sticky="ew")
            self.buttons[key] = btn

    def _switch(self, key):
        if self.current == key:
            return
        self.current = key

        # Update all buttons
        for mat_key, btn in self.buttons.items():
            if mat_key == key:
                btn.configure(fg_color="#0891b2", border_width=0)
            else:
                btn.configure(fg_color="#2d3748", border_width=2)

        self.callback(key)
