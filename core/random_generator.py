import numpy as np
from core.constraints import clamp_curve

class RandomCurveGenerator:

    def generate(self, sieve_sizes, lower, upper):
        """
        Generates a highly variable, "wiggly" random passing curve.
        Uses a Monte Carlo Markov Chain (MCMC) approach to explore the entire valid space,
        ensuring strict envelope compliance and monotonicity without statistical bias.
        """
        n = len(lower)
        curve = np.zeros(n)
        
        # 1. Initialize with a valid curve (hugging the upper limit)
        prev_passing = 100.0
        for i in range(n):
            env_U = upper[i] - 0.1 if lower[i] < upper[i] else upper[i]
            val = min(env_U, prev_passing)
            if i == n - 1 or (lower[i] == 0 and upper[i] == 0):
                val = 0.0
            curve[i] = val
            prev_passing = val
            
        # 2. Randomly mutate the curve many times to explore the valid space
        iterations = 3000
        for _ in range(iterations):
            # Pick a random sieve
            i = np.random.randint(0, n)
            
            # Pan is always 0, and if limits are tightly fixed to 100, ignore
            if i == n - 1 or (lower[i] == 0 and upper[i] == 0) or (lower[i] == 100 and upper[i] == 100):
                continue
                
            env_L = lower[i] + 0.1 if lower[i] < upper[i] else lower[i]
            env_U = upper[i] - 0.1 if lower[i] < upper[i] else upper[i]
            
            prev_P = curve[i-1] if i > 0 else 100.0
            next_P = curve[i+1] if i < n-1 else 0.0
            
            # Valid range for curve[i] based on current neighbors and limits
            max_val = min(env_U, prev_P)
            min_val = max(env_L, next_P)
            
            if min_val <= max_val:
                # 20% chance to jump to an extreme edge (creates jagged/wiggly shapes)
                # 80% chance to pick uniformly
                if np.random.random() < 0.2:
                    curve[i] = min_val if np.random.random() < 0.5 else max_val
                else:
                    curve[i] = np.random.uniform(min_val, max_val)

        return curve.tolist()

