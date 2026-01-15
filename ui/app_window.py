import customtkinter as ctk
from ui.tabs import TopTabs
from ui.input_panel import InputPanel
from ui.graph_panel import GraphPanel
from ui.table_panel import TablePanel
from ui.footer import Footer
from core.total_weight import TotalWeightManager
import os
import sys

class GradationApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Create shared total weight manager for all components
        self.total_weight_manager = TotalWeightManager()

        # Set dark theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Window setup
        self.title("Gradation Analysis")
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
        self.grid_rowconfigure(3, weight=0)

        # TOP TABS
        self.tabs = TopTabs(self, self._on_material_change)
        self.tabs.grid(row=0, column=0, columnspan=2, sticky="ew")

        # LEFT INPUT PANEL
        self.input_panel = InputPanel(self, self.total_weight_manager)
        self.input_panel.grid(row=1, column=0, sticky="nsw", padx=10, pady=10)

        # RIGHT GRAPH PANEL
        self.graph_panel = GraphPanel(self)
        self.graph_panel.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        # BOTTOM TABLE PANEL
        self.table_panel = TablePanel(self, self.total_weight_manager)
        self.table_panel.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(0,10))

        # FOOTER (Instagram/GitHub) - grid instead of place to avoid overlap
        footer = Footer(self)
        footer.grid(row=3, column=0, columnspan=2, sticky="e", padx=10, pady=(5,5))

        # Initialize with Fine Aggregate data
        self._on_material_change("fine")
        
        # Handle window close event
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_closing(self):
        """
        Properly close the application and all resources
        """
        try:
            # Close matplotlib figure if it exists
            if hasattr(self.graph_panel, 'figure'):
                import matplotlib.pyplot as plt
                plt.close(self.graph_panel.figure)
        except:
            pass
        
        try:
            # Destroy the window
            self.destroy()
        except:
            pass
        
        # Force exit to ensure no background processes remain
        sys.exit(0)


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
        # Load table first to initialize retained values
        self.table_panel.load_material(material_key)
        # Then load other panels
        self.input_panel.load_material(material_key)
        self.graph_panel.load_material(material_key)
