import customtkinter as ctk
from src.ui.main_window import MainWindow

# Set appearance mode and default color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def main():
    app = ctk.CTk()
    app.title("Gradation Analysis")
    app.geometry("1200x700")
    app.minsize(1000, 600)
    
    # Create main window
    window = MainWindow(app)
    window.pack(fill="both", expand=True)
    
    app.mainloop()

if __name__ == "__main__":
    main()