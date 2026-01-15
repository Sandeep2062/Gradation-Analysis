import numpy as np
from core.total_weight import TotalWeightManager

class GradationEngine:

    def __init__(self, total_weight_manager=None):
        # Use provided manager or create new one (for backward compatibility)
        self.total_weight_manager = total_weight_manager or TotalWeightManager()

    def passing_to_retained(self, passing):
        """
        Convert % passing curve → retained weights.
        """
        passing = np.array(passing, dtype=float)

        # Convert passing to fraction
        frac_pass = passing / 100.0

        # Compute retained fraction = difference between passes
        retained_frac = np.zeros_like(frac_pass)

        # Material retained at each sieve = P(previous) - P(current)
        retained_frac[0] = 1 - frac_pass[0]
        for i in range(1, len(frac_pass)):
            retained_frac[i] = frac_pass[i-1] - frac_pass[i]

        retained_frac = np.clip(retained_frac, 0, None)

        # Scale to total weight
        total_wt = self.total_weight_manager.get_total_weight()
        retained_weights = retained_frac * total_wt

        return retained_weights.tolist()
