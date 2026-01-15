import numpy as np

def clamp_curve(curve, lower, upper):
    curve = np.array(curve, dtype=float)
    lower = np.array(lower, dtype=float)
    upper = np.array(upper, dtype=float)

    return np.clip(curve, lower, upper)
