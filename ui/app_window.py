import customtkinter as ctk
from ui.tabs import TopTabs
from ui.input_panel import InputPanel
from ui.graph_panel import GraphPanel
from ui.table_panel import TablePanel
from ui.footer import Footer

class GradationApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Set dark theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Window setup
        self.title("Gradation Analysis")
        self.geometry("1300x780")
        self.minsize(1200, 700)
        self.configure(fg_color="#0f172a")

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

    def _on_material_change(self, material_key):
        """
        Triggered when user switches tabs (Fine Aggregate / Sub-Base)
        """
        self.input_panel.load_material(material_key)
        self.graph_panel.load_material(material_key)
        self.table_panel.load_material(material_key)
