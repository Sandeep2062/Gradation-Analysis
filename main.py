import customtkinter as ctk
from ui.app_window import GradationApp

# Dark theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

if __name__ == "__main__":
    app = GradationApp()
    app.mainloop()
