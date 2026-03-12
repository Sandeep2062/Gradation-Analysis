import customtkinter as ctk

class TopTabs(ctk.CTkFrame):

    def __init__(self, parent, callback):
        super().__init__(parent, fg_color="#0f172a")

        self.callback = callback
        self.materials = {
            "fine": "Coarse Sand",
            "finesand": "Fine Sand",
            "coarse1": "Coarse Aggregate 1",
            "coarse2": "Coarse Aggregate 2",
            "subbase": "Sub-Base",
            "crm": "CRM for Base",
            "agg40": "Aggregate 40 mm",
            "agg20": "Aggregate 20 mm"
        }

        self.current = "fine"
        self.buttons = {}

        self._build_tabs()

    def _build_tabs(self):
        tabs_data = [
            ("fine", "⚙️ Coarse Sand"),
            ("finesand", "⚙️ Fine Sand"),
            ("coarse1", "🏔️ Coarse Agg. 1"),
            ("coarse2", "🏔️ Coarse Agg. 2"),
            ("agg40", "🪨 Aggregate 40 mm"),
            ("agg20", "🪨 Aggregate 20 mm"),
            ("crm", "🔨 CRM for Base"),
            ("subbase", "🏗️ Sub-Base")
        ]

        # Dynamic grid configuration for all tabs
        for i in range(len(tabs_data)):
            self.grid_columnconfigure(i, weight=1)

        for idx, (key, label) in enumerate(tabs_data):
            is_active = key == "fine"
            btn = ctk.CTkButton(
                self,
                text=label,
                corner_radius=10,
                height=40,
                fg_color="#0891b2" if is_active else "#1e293b",
                border_width=0 if is_active else 1,
                border_color="#334155" if not is_active else None,
                text_color="white" if is_active else "#94a3b8",
                font=("Segoe UI", 12, "bold"),
                hover_color="#0ea5e9" if is_active else "#334155",
                command=lambda k=key: self._switch(k)
            )
            btn.grid(row=0, column=idx, padx=4, pady=10, sticky="ew")
            self.buttons[key] = btn

    def _switch(self, key):
        if self.current == key:
            return
        self.current = key

        # Update all buttons with active/inactive states
        for mat_key, btn in self.buttons.items():
            if mat_key == key:
                btn.configure(
                    fg_color="#0891b2", border_width=0,
                    text_color="white", hover_color="#0ea5e9"
                )
            else:
                btn.configure(
                    fg_color="#1e293b", border_width=1,
                    text_color="#94a3b8", hover_color="#334155"
                )

        self.callback(key)
