import customtkinter as ctk
from tkinter import messagebox

class TablePanel(ctk.CTkFrame):
    def __init__(self, parent, graph_panel):
        super().__init__(parent)
        
        self.graph_panel = graph_panel
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create scrollable frame
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Create table headers
        headers_frame = ctk.CTkFrame(self.scroll_frame)
        headers_frame.pack(fill="x", padx=5, pady=5)
        
        headers_frame.grid_columnconfigure(0, weight=1)
        headers_frame.grid_columnconfigure(1, weight=1)
        headers_frame.grid_columnconfigure(2, weight=1)
        
        sieve_label = ctk.CTkLabel(headers_frame, text="Sieve Size (mm)", font=ctk.CTkFont(weight="bold"))
        sieve_label.grid(row=0, column=0, padx=10, pady=5)
        
        passing_label = ctk.CTkLabel(headers_frame, text="Passing (%)", font=ctk.CTkFont(weight="bold"))
        passing_label.grid(row=0, column=1, padx=10, pady=5)
        
        retained_label = ctk.CTkLabel(headers_frame, text="Retained (%)", font=ctk.CTkFont(weight="bold"))
        retained_label.grid(row=0, column=2, padx=10, pady=5)
        
        # Table data
        self.sieve_labels = []
        self.passing_entries = []
        self.retained_labels = []
    
    def update_table(self, sieve_sizes, passing):
        # Clear existing data
        for widget in self.scroll_frame.winfo_children():
            if widget != self.scroll_frame.winfo_children()[0]:  # Keep headers
                widget.destroy()
        
        self.sieve_labels = []
        self.passing_entries = []
        self.retained_labels = []
        
        # Add data rows
        cumulative_passing = 100
        for i, (sieve, pass_val) in enumerate(zip(sieve_sizes, passing)):
            row_frame = ctk.CTkFrame(self.scroll_frame)
            row_frame.pack(fill="x", padx=5, pady=2)
            
            row_frame.grid_columnconfigure(0, weight=1)
            row_frame.grid_columnconfigure(1, weight=1)
            row_frame.grid_columnconfigure(2, weight=1)
            
            # Sieve size
            sieve_label = ctk.CTkLabel(row_frame, text=str(sieve))
            sieve_label.grid(row=0, column=0, padx=10, pady=5)
            self.sieve_labels.append(sieve_label)
            
            # Passing entry
            passing_entry = ctk.CTkEntry(row_frame)
            passing_entry.insert(0, str(pass_val))
            passing_entry.grid(row=0, column=1, padx=10, pady=5)
            passing_entry.bind("<Return>", lambda e, idx=i: self.on_passing_change(idx))
            self.passing_entries.append(passing_entry)
            
            # Retained label
            retained_percent = cumulative_passing - pass_val
            retained_label = ctk.CTkLabel(row_frame, text=f"{retained_percent:.2f}")
            retained_label.grid(row=0, column=2, padx=10, pady=5)
            self.retained_labels.append(retained_label)
            
            cumulative_passing = pass_val
    
    def on_passing_change(self, index):
        try:
            # Get new passing value
            new_passing = float(self.passing_entries[index].get())
            
            # Clamp to limits
            lower = self.graph_panel.lower_limits[index]
            upper = self.graph_panel.upper_limits[index]
            new_passing = max(lower, min(upper, new_passing))
            
            # Update passing value
            self.graph_panel.passing[index] = new_passing
            
            # Update graph
            self.graph_panel.update_passing(self.graph_panel.passing)
            
            # Update table
            self.update_table(self.graph_panel.sieve_sizes, self.graph_panel.passing)
            
            # Update FM if available
            if hasattr(self.master, 'update_fm'):
                self.master.update_fm()
            elif hasattr(self.master.master, 'update_fm'):
                self.master.master.update_fm()
                
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
            self.passing_entries[index].delete(0, "end")
            self.passing_entries[index].insert(0, str(self.graph_panel.passing[index]))