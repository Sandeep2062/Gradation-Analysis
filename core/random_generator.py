import numpy as np
from core.constraints import clamp_curve

class RandomCurveGenerator:

    def generate(self, sieve_sizes, lower, upper):
        """
        Generates a smooth random passing curve within limits.
        """

        lower = np.array(lower, dtype=float)
        upper = np.array(upper, dtype=float)

        n = len(lower)

        # Start with midpoint between lower and upper
        curve = (lower + upper) / 2

        # Add smooth random noise
        noise = np.random.normal(0, 3, n)  # small noise
        noise = np.cumsum(noise)           # accumulate → smooth
        noise = noise - np.mean(noise)     # center

        curve = curve + noise

        # Clamp inside limits
        curve = clamp_curve(curve, lower, upper)

        # Final smoothing pass
        for i in range(1, n-1):
            curve[i] = (curve[i-1] + curve[i] + curve[i+1]) / 3

        return curve.tolist()
