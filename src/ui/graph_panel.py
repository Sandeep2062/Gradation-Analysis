import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np
import customtkinter as ctk
from matplotlib.patches import Polygon

class GraphPanel(ctk.CTkFrame):
    def __init__(self, parent, material_model):
        super().__init__(parent)
        
        self.material_model = material_model
        
        # Data storage
        self.sieve_sizes = []
        self.lower_limits = []
        self.upper_limits = []
        self.passing = []
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Create toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        
        # Setup plot
        self.setup_plot()
        
        # Bind events
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        
        # Dragging state
        self.dragging = False
        self.drag_index = None
    
    def setup_plot(self):
        self.ax.set_xlabel('Sieve Size (mm)')
        self.ax.set_ylabel('Passing (%)')
        self.ax.set_title('Gradation Analysis')
        self.ax.grid(True, linestyle='--', alpha=0.6)
        self.ax.set_xscale('log')
        
        # Initialize empty lines
        self.lower_line, = self.ax.plot([], [], 'r--', label='Lower Limit')
        self.upper_line, = self.ax.plot([], [], 'g--', label='Upper Limit')
        self.passing_line, = self.ax.plot([], [], 'b-', label='Obtained', marker='o')
        
        # Create draggable points
        self.drag_points, = self.ax.plot([], [], 'bo', markersize=8)
        
        # Create shaded area between limits
        self.limit_area = None
        
        self.ax.legend()
        self.fig.tight_layout()
    
    def set_data(self, sieve_sizes, lower_limits, upper_limits, passing):
        self.sieve_sizes = sieve_sizes
        self.lower_limits = lower_limits
        self.upper_limits = upper_limits
        self.passing = passing
        
        self.update_plot()
    
    def update_plot(self):
        # Update lines
        self.lower_line.set_data(self.sieve_sizes, self.lower_limits)
        self.upper_line.set_data(self.sieve_sizes, self.upper_limits)
        self.passing_line.set_data(self.sieve_sizes, self.passing)
        
        # Update draggable points
        self.drag_points.set_data(self.sieve_sizes, self.passing)
        
        # Update shaded area
        if self.limit_area:
            self.limit_area.remove()
        
        vertices = []
        for i in range(len(self.sieve_sizes)):
            vertices.append((self.sieve_sizes[i], self.lower_limits[i]))
        for i in range(len(self.sieve_sizes)-1, -1, -1):
            vertices.append((self.sieve_sizes[i], self.upper_limits[i]))
        
        self.limit_area = Polygon(vertices, alpha=0.2, color='green')
        self.ax.add_patch(self.limit_area)
        
        # Adjust axis limits
        self.ax.relim()
        self.ax.autoscale_view()
        
        # Redraw
        self.canvas.draw()
    
    def update_passing(self, passing):
        self.passing = passing
        self.passing_line.set_data(self.sieve_sizes, self.passing)
        self.drag_points.set_data(self.sieve_sizes, self.passing)
        self.canvas.draw()
    
    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        
        # Check if click is near a point
        for i, (x, y) in enumerate(zip(self.sieve_sizes, self.passing)):
            # Convert to screen coordinates
            display_coords = self.ax.transData.transform((x, y))
            
            # Calculate distance
            dist = np.sqrt((event.x - display_coords[0])**2 + 
                          (event.y - display_coords[1])**2)
            
            if dist < 10:  # Threshold for clicking
                self.dragging = True
                self.drag_index = i
                break
    
    def on_motion(self, event):
        if not self.dragging or self.drag_index is None or event.inaxes != self.ax:
            return
        
        # Get new y value
        new_y = event.ydata
        
        # Clamp to limits
        lower = self.lower_limits[self.drag_index]
        upper = self.upper_limits[self.drag_index]
        new_y = max(lower, min(upper, new_y))
        
        # Update passing value
        self.passing[self.drag_index] = new_y
        
        # Update plot
        self.update_passing(self.passing)
        
        # Notify parent of change
        if hasattr(self.master, 'update_table'):
            self.master.update_table(self.sieve_sizes, self.passing)
        elif hasattr(self.master.master, 'update_table'):
            self.master.master.update_table(self.sieve_sizes, self.passing)
    
    def on_release(self, event):
        self.dragging = False
        self.drag_index = None