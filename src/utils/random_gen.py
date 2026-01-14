import numpy as np

def generate_random_curve(lower_limits, upper_limits):
    """Generate a random curve between lower and upper limits"""
    # Ensure smoothness by using interpolation
    n_points = len(lower_limits)
    
    # Generate random points within limits
    random_points = []
    for i in range(n_points):
        lower = lower_limits[i]
        upper = upper_limits[i]
        random_points.append(np.random.uniform(lower, upper))
    
    # Apply smoothing
    smoothed_points = smooth_curve(random_points)
    
    # Ensure points stay within limits
    for i in range(n_points):
        smoothed_points[i] = max(lower_limits[i], min(upper_limits[i], smoothed_points[i]))
    
    return smoothed_points

def smooth_curve(points, window_size=3):
    """Apply a simple moving average smoothing to a curve"""
    if len(points) < window_size:
        return points
    
    smoothed = []
    half_window = window_size // 2
    
    for i in range(len(points)):
        start = max(0, i - half_window)
        end = min(len(points), i + half_window + 1)
        window = points[start:end]
        smoothed.append(sum(window) / len(window))
    
    return smoothed