import customtkinter as ctk
import webbrowser

class Footer(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        # Container frame for links
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(padx=10, pady=10)

        # Instagram link
        instagram_btn = ctk.CTkButton(
            container,
            text="📸 Instagram",
            fg_color="#e1306c",
            hover_color="#c13584",
            text_color="white",
            corner_radius=8,
            height=32,
            command=lambda: webbrowser.open("https://instagram.com/sandeep._.2062")
        )
        instagram_btn.pack(side="left", padx=5)

        # GitHub link
        github_btn = ctk.CTkButton(
            container,
            text="🐙 GitHub",
            fg_color="#333333",
            hover_color="#555555",
            text_color="white",
            corner_radius=8,
            height=32,
            command=lambda: webbrowser.open("https://github.com/Sandeep2062/Gradation-Analysis")
        )
        github_btn.pack(side="left", padx=5)
