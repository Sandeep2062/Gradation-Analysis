import numpy as np
from core.constraints import clamp_curve

class RandomCurveGenerator:

    def generate(self, sieve_sizes, lower, upper):
        """
        Generates a smooth random passing curve within limits.
        Ensures the curve stays strictly within upper and lower bounds.
        """

        lower = np.array(lower, dtype=float)
        upper = np.array(upper, dtype=float)

        n = len(lower)

        # Start with midpoint between lower and upper
        curve = (lower + upper) / 2

        # Add smooth random noise with smaller magnitude
        noise = np.random.normal(0, 2, n)  # reduced noise magnitude
        noise = np.cumsum(noise)           # accumulate → smooth
        noise = noise - np.mean(noise)     # center

        curve = curve + noise

        # Clamp inside limits STRICTLY
        curve = np.clip(curve, lower, upper)

        # Apply multiple smoothing passes to reduce abrupt changes
        for _ in range(3):
            smoothed = np.copy(curve)
            for i in range(1, n-1):
                smoothed[i] = (curve[i-1] + curve[i] + curve[i+1]) / 3
            curve = smoothed

        # Final clamp to ensure we're still within limits after smoothing
        curve = np.clip(curve, lower, upper)

        return curve.tolist()

