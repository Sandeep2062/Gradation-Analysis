import customtkinter as ctk

class Footer(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        label = ctk.CTkLabel(
            self,
            text="Instagram: @sandeep._.2062   |   GitHub: Sandeep2062 / Gradation-Analysis",
            font=("Segoe UI", 12),
            text_color="#64748b"
        )
        label.pack(padx=10, pady=10)
