import customtkinter as ctk
from ui.tabs import TopTabs
from ui.input_panel import InputPanel
from ui.graph_panel import GraphPanel
from ui.table_panel import TablePanel
from ui.footer import Footer
import os
import sys
import subprocess

class GradationApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        
        # Get version from git tag
        self.version = self._get_version()

        # Set dark theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Window setup
        self.title(f"Gradation Analysis {self.version}")
        self.geometry("1400x850")
        self.minsize(1200, 750)
        self.configure(fg_color="#0f1419")
        
        # Set icon - handle both development and bundled environments
        self._set_icon()

        # GRID LAYOUT
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        # TOP TABS
        self.tabs = TopTabs(self, self._on_material_change)
        self.tabs.grid(row=0, column=0, columnspan=2, sticky="ew")

        # LEFT INPUT PANEL
        self.input_panel = InputPanel(self)
        self.input_panel.grid(row=1, column=0, sticky="nsw", padx=10, pady=10)

        # RIGHT GRAPH PANEL
        self.graph_panel = GraphPanel(self)
        self.graph_panel.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        # BOTTOM TABLE PANEL
        self.table_panel = TablePanel(self)
        self.table_panel.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(0,10))

        # FOOTER (Instagram/GitHub)
        Footer(self).place(relx=1.0, rely=1.0, anchor="se")

        # Initialize with Fine Aggregate data
        self._on_material_change("fine")

    def _set_icon(self):
        """
        Set window icon - works in both development and PyInstaller bundled environments
        """
        try:
            # Try development path first
            dev_icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icon.ico")
            
            # Try PyInstaller bundled path
            if getattr(sys, 'frozen', False):
                # App is run as compiled (PyInstaller)
                base_path = sys._MEIPASS
                bundled_icon_path = os.path.join(base_path, "assets", "icon.ico")
                if os.path.exists(bundled_icon_path):
                    self.iconbitmap(bundled_icon_path)
                    return
            
            # Try development path
            if os.path.exists(dev_icon_path):
                self.iconbitmap(dev_icon_path)
                return
                
        except Exception as e:
            # Silently fail if icon cannot be set (not critical)
            pass

    def _on_material_change(self, material_key):
        """
        Triggered when user switches tabs (Fine Aggregate / Sub-Base / Coarse Aggregate / CRM for Base)
        """
        self.input_panel.load_material(material_key)
        self.graph_panel.load_material(material_key)
        self.table_panel.load_material(material_key)
    def _get_version(self):
        """
        Get the latest git tag as version (e.g., v1.2)
        Falls back to 'v0.0' if no tag is found
        """
        try:
            version = subprocess.check_output(
                ["git", "describe", "--tags", "--abbrev=0"],
                stderr=subprocess.DEVNULL,
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ).decode("utf-8").strip()
            return version
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "v0.0"