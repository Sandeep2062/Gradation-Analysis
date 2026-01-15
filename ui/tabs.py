import customtkinter as ctk

class TopTabs(ctk.CTkFrame):

    def __init__(self, parent, callback):
        super().__init__(parent, fg_color="#1e293b")

        self.callback = callback
        self.materials = {
            "fine": "Fine Aggregate",
            "subbase": "Sub-Base"
        }

        self.current = "fine"

        self._build_tabs()

    def _build_tabs(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.btn_fine = ctk.CTkButton(
            self,
            text="⚙️ Fine Aggregate",
            corner_radius=20,
            fg_color="#0891b2",
            hover_color="#0ea5e9",
            text_color="white",
            font=("Segoe UI", 14, "bold"),
            command=lambda: self._switch("fine")
        )
        self.btn_fine.grid(row=0, column=0, padx=10, pady=12, sticky="ew")

        self.btn_subbase = ctk.CTkButton(
            self,
            text="🏗️ Sub-Base",
            corner_radius=20,
            fg_color="transparent",
            border_width=2,
            border_color="#0891b2",
            text_color="white",
            font=("Segoe UI", 14, "bold"),
            hover_color="#1e293b",
            command=lambda: self._switch("subbase")
        )
        self.btn_subbase.grid(row=0, column=1, padx=10, pady=12, sticky="ew")

    def _switch(self, key):
        if self.current == key:
            return
        self.current = key

        # Active tab glow
        if key == "fine":
            self.btn_fine.configure(fg_color="#0891b2", border_width=0)
            self.btn_subbase.configure(fg_color="transparent", border_width=2)
        else:
            self.btn_subbase.configure(fg_color="#0891b2", border_width=0)
            self.btn_fine.configure(fg_color="transparent", border_width=2)

        self.callback(key)
