import customtkinter as ctk
from tkinter import messagebox
from src.ui.graph_panel import GraphPanel
from src.ui.table_panel import TablePanel
from src.data.models import FineAggregate, SubBase
from src.utils.clipboard import copy_to_clipboard
from src.utils.random_gen import generate_random_curve

class MainWindow(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create tabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Add tabs
        self.fine_aggregate_tab = self.tabview.add("Fine Aggregate")
        self.sub_base_tab = self.tabview.add("Sub-Base")
        
        # Create panels for each tab
        self.create_fine_aggregate_tab()
        self.create_sub_base_tab()
        
        # Create header with social links
        self.create_header()
        
        # Create footer
        self.create_footer()
    
    def create_header(self):
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="Gradation Analysis", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=10)
    
    def create_footer(self):
        footer_frame = ctk.CTkFrame(self)
        footer_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        social_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
        social_frame.pack(pady=10)
        
        github_label = ctk.CTkLabel(
            social_frame,
            text="GitHub: Sandeep2062/Gradation-Analysis",
            font=ctk.CTkFont(size=12)
        )
        github_label.pack(side="left", padx=20)
        
        insta_label = ctk.CTkLabel(
            social_frame,
            text="Instagram: @yourusername",  # Replace with your actual username
            font=ctk.CTkFont(size=12)
        )
        insta_label.pack(side="left", padx=20)
    
    def create_fine_aggregate_tab(self):
        # Configure grid
        self.fine_aggregate_tab.grid_columnconfigure(0, weight=1)
        self.fine_aggregate_tab.grid_columnconfigure(1, weight=3)
        self.fine_aggregate_tab.grid_rowconfigure(0, weight=1)
        
        # Create left panel
        left_panel = ctk.CTkFrame(self.fine_aggregate_tab)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        left_panel.grid_columnconfigure(0, weight=1)
        
        # Total weight input
        weight_frame = ctk.CTkFrame(left_panel)
        weight_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        weight_label = ctk.CTkLabel(weight_frame, text="Total Weight (g):")
        weight_label.pack(pady=(10, 0))
        
        self.fine_weight_entry = ctk.CTkEntry(weight_frame)
        self.fine_weight_entry.pack(pady=5)
        self.fine_weight_entry.insert(0, "2000")
        
        # Random generator button
        random_btn = ctk.CTkButton(
            left_panel,
            text="Generate Random Curve",
            command=self.generate_fine_random_curve
        )
        random_btn.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        
        # Copy button
        copy_btn = ctk.CTkButton(
            left_panel,
            text="Copy Weight Retained",
            command=self.copy_fine_weight_retained
        )
        copy_btn.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        
        # FM display
        fm_frame = ctk.CTkFrame(left_panel)
        fm_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        
        fm_label = ctk.CTkLabel(fm_frame, text="Fineness Modulus:")
        fm_label.pack(pady=(10, 0))
        
        self.fine_fm_label = ctk.CTkLabel(fm_frame, text="0.00", font=ctk.CTkFont(size=16, weight="bold"))
        self.fine_fm_label.pack(pady=5)
        
        # Create graph panel
        self.fine_graph_panel = GraphPanel(self.fine_aggregate_tab, FineAggregate())
        self.fine_graph_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        
        # Create table panel
        self.fine_table_panel = TablePanel(self.fine_aggregate_tab, self.fine_graph_panel)
        self.fine_table_panel.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
        
        # Initialize with sample data
        self.initialize_fine_aggregate()
    
    def create_sub_base_tab(self):
        # Configure grid
        self.sub_base_tab.grid_columnconfigure(0, weight=1)
        self.sub_base_tab.grid_columnconfigure(1, weight=3)
        self.sub_base_tab.grid_rowconfigure(0, weight=1)
        
        # Create left panel
        left_panel = ctk.CTkFrame(self.sub_base_tab)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        left_panel.grid_columnconfigure(0, weight=1)
        
        # Total weight input
        weight_frame = ctk.CTkFrame(left_panel)
        weight_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        weight_label = ctk.CTkLabel(weight_frame, text="Total Weight (g):")
        weight_label.pack(pady=(10, 0))
        
        self.sub_weight_entry = ctk.CTkEntry(weight_frame)
        self.sub_weight_entry.pack(pady=5)
        self.sub_weight_entry.insert(0, "2000")
        
        # Random generator button
        random_btn = ctk.CTkButton(
            left_panel,
            text="Generate Random Curve",
            command=self.generate_sub_random_curve
        )
        random_btn.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        
        # Copy button
        copy_btn = ctk.CTkButton(
            left_panel,
            text="Copy Weight Retained",
            command=self.copy_sub_weight_retained
        )
        copy_btn.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        
        # FM display
        fm_frame = ctk.CTkFrame(left_panel)
        fm_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        
        fm_label = ctk.CTkLabel(fm_frame, text="Fineness Modulus:")
        fm_label.pack(pady=(10, 0))
        
        self.sub_fm_label = ctk.CTkLabel(fm_frame, text="0.00", font=ctk.CTkFont(size=16, weight="bold"))
        self.sub_fm_label.pack(pady=5)
        
        # Create graph panel
        self.sub_graph_panel = GraphPanel(self.sub_base_tab, SubBase())
        self.sub_graph_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        
        # Create table panel
        self.sub_table_panel = TablePanel(self.sub_base_tab, self.sub_graph_panel)
        self.sub_table_panel.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
        
        # Initialize with sample data
        self.initialize_sub_base()
    
    def initialize_fine_aggregate(self):
        # Sample data for fine aggregate
        sieve_sizes = [4.75, 2.36, 1.18, 0.6, 0.3, 0.15, 0.075, 0]
        lower_limits = [100, 95, 85, 70, 45, 20, 5, 0]
        upper_limits = [100, 100, 100, 95, 75, 40, 15, 0]
        passing = [100, 97, 90, 80, 60, 30, 10, 0]
        
        self.fine_graph_panel.set_data(sieve_sizes, lower_limits, upper_limits, passing)
        self.fine_table_panel.update_table(sieve_sizes, passing)
        self.update_fine_fm()
    
    def initialize_sub_base(self):
        # Sample data for sub-base
        sieve_sizes = [37.5, 25, 19, 12.5, 9.5, 4.75, 2.36, 0.075, 0]
        lower_limits = [100, 95, 85, 70, 60, 40, 25, 5, 0]
        upper_limits = [100, 100, 100, 95, 85, 65, 45, 15, 0]
        passing = [100, 98, 92, 82, 72, 50, 35, 10, 0]
        
        self.sub_graph_panel.set_data(sieve_sizes, lower_limits, upper_limits, passing)
        self.sub_table_panel.update_table(sieve_sizes, passing)
        self.update_sub_fm()
    
    def generate_fine_random_curve(self):
        try:
            total_weight = float(self.fine_weight_entry.get())
            passing = generate_random_curve(
                self.fine_graph_panel.lower_limits,
                self.fine_graph_panel.upper_limits
            )
            self.fine_graph_panel.update_passing(passing)
            self.fine_table_panel.update_table(self.fine_graph_panel.sieve_sizes, passing)
            self.update_fine_fm()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid total weight")
    
    def generate_sub_random_curve(self):
        try:
            total_weight = float(self.sub_weight_entry.get())
            passing = generate_random_curve(
                self.sub_graph_panel.lower_limits,
                self.sub_graph_panel.upper_limits
            )
            self.sub_graph_panel.update_passing(passing)
            self.sub_table_panel.update_table(self.sub_graph_panel.sieve_sizes, passing)
            self.update_sub_fm()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid total weight")
    
    def copy_fine_weight_retained(self):
        try:
            total_weight = float(self.fine_weight_entry.get())
            weight_retained = self.calculate_weight_retained(
                self.fine_graph_panel.passing,
                total_weight
            )
            copy_to_clipboard(weight_retained)
            messagebox.showinfo("Success", "Weight retained values copied to clipboard")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid total weight")
    
    def copy_sub_weight_retained(self):
        try:
            total_weight = float(self.sub_weight_entry.get())
            weight_retained = self.calculate_weight_retained(
                self.sub_graph_panel.passing,
                total_weight
            )
            copy_to_clipboard(weight_retained)
            messagebox.showinfo("Success", "Weight retained values copied to clipboard")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid total weight")
    
    def calculate_weight_retained(self, passing, total_weight):
        # Calculate weight retained from passing percentages
        weight_retained = []
        cumulative_passing = 100
        
        for p in passing:
            retained_percent = cumulative_passing - p
            retained_weight = total_weight * retained_percent / 100
            weight_retained.append(retained_weight)
            cumulative_passing = p
        
        return weight_retained
    
    def update_fine_fm(self):
        fm = self.calculate_fm(self.fine_graph_panel.passing)
        self.fine_fm_label.configure(text=f"{fm:.2f}")
    
    def update_sub_fm(self):
        fm = self.calculate_fm(self.sub_graph_panel.passing)
        self.sub_fm_label.configure(text=f"{fm:.2f}")
    
    def calculate_fm(self, passing):
        # Calculate fineness modulus
        cumulative_retained = [100 - p for p in passing]
        # Sum of cumulative retained divided by 100
        fm = sum(cumulative_retained) / 100
        return fm