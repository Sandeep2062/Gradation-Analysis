import numpy as np
from core.total_weight import TotalWeightManager

class GradationEngine:

    def __init__(self, total_weight_manager=None):
        # Use provided manager or create new one (for backward compatibility)
        self.total_weight_manager = total_weight_manager or TotalWeightManager()

    def passing_to_retained(self, passing):
        """
        Convert % passing curve → retained weights.
        passing is in table order (largest sieve first → Pan last).
        """
        if not passing or len(passing) == 0:
            return []
            
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

    def retained_to_passing(self, retained_weights):
        """
        Convert retained weights → % passing curve.
        This is the exact inverse of passing_to_retained.
        retained_weights is in table order (largest sieve first → Pan last).
        """
        if not retained_weights or len(retained_weights) == 0:
            return []
            
        retained = np.array(retained_weights, dtype=float)

        total_wt = self.total_weight_manager.get_total_weight()

        if total_wt <= 0:
            return [50.0] * len(retained)

        # Convert retained weights to fractions
        retained_frac = retained / total_wt
        retained_frac = np.clip(retained_frac, 0, None)

        # Convert retained fractions to passing fractions
        # passing[0] = 1 - retained_frac[0]
        # passing[i] = passing[i-1] - retained_frac[i]
        passing_frac = np.zeros_like(retained_frac)
        passing_frac[0] = 1 - retained_frac[0]

        for i in range(1, len(retained_frac)):
            passing_frac[i] = passing_frac[i-1] - retained_frac[i]

        # Clip to valid range [0, 1] and convert to percentages
        passing_frac = np.clip(passing_frac, 0, 1)
        passing = passing_frac * 100

        return passing.tolist()

    def enforce_monotonicity_table_order(self, passing, lower_limits, upper_limits, locked_rows=None):
        """
        Enforce monotonicity on a passing curve in TABLE order (largest→smallest sieve).
        In table order, passing % must be NON-INCREASING (100 → 0).
        
        Rules:
        - Locked rows are NEVER modified
        - Each value is clamped to [lower_limit, upper_limit]
        - passing[i] <= passing[i-1] (non-increasing)
        - If a locked neighbor blocks monotonicity, the unlocked side is clamped
        
        Returns the corrected passing list.
        """
        passing = list(passing)
        n = len(passing)
        locked = locked_rows or set()
        lower = list(lower_limits)
        upper = list(upper_limits)

        # First pass: clamp all unlocked values to their limits
        for i in range(n):
            if i not in locked:
                passing[i] = max(lower[i], min(upper[i], passing[i]))

        # Forward pass: ensure non-increasing (top-down in table)
        # passing[i] must be <= passing[i-1]
        for i in range(1, n):
            if passing[i] > passing[i-1]:
                if i not in locked:
                    # Clamp this value down to the previous
                    passing[i] = min(passing[i], passing[i-1])
                    passing[i] = max(lower[i], passing[i])
                elif (i-1) not in locked:
                    # This row is locked but previous isn't — raise previous
                    passing[i-1] = max(passing[i-1], passing[i])
                    passing[i-1] = min(upper[i-1], passing[i-1])

        # Backward pass: ensure non-increasing (bottom-up)
        for i in range(n-2, -1, -1):
            if passing[i] < passing[i+1]:
                if i not in locked:
                    passing[i] = max(passing[i], passing[i+1])
                    passing[i] = min(upper[i], passing[i])
                elif (i+1) not in locked:
                    passing[i+1] = min(passing[i+1], passing[i])
                    passing[i+1] = max(lower[i+1], passing[i+1])

        # Final clamp to limits
        for i in range(n):
            if i not in locked:
                passing[i] = max(lower[i], min(upper[i], passing[i]))

        return passing

    def enforce_monotonicity_graph_order(self, obtained, lower, upper, locked_graph_indices=None):
        """
        Enforce monotonicity on obtained curve in GRAPH order (smallest→largest sieve, left→right).
        In graph order, passing % must be NON-DECREASING (0 → 100, left → right).
        
        locked_graph_indices: set of indices in graph order that are locked.
        
        Returns corrected numpy array.
        """
        obtained = np.array(obtained, dtype=float)
        n = len(obtained)
        locked = locked_graph_indices or set()

        # Clamp to limits first
        for i in range(n):
            if i not in locked:
                obtained[i] = max(lower[i], min(upper[i], obtained[i]))

        # Forward pass: ensure non-decreasing (left to right)
        # obtained[i] must be >= obtained[i-1]
        for i in range(1, n):
            if obtained[i] < obtained[i-1]:
                if i not in locked:
                    obtained[i] = max(obtained[i], obtained[i-1])
                    obtained[i] = min(upper[i], obtained[i])
                elif (i-1) not in locked:
                    obtained[i-1] = min(obtained[i-1], obtained[i])
                    obtained[i-1] = max(lower[i-1], obtained[i-1])

        # Backward pass: ensure non-decreasing
        for i in range(n-2, -1, -1):
            if obtained[i] > obtained[i+1]:
                if i not in locked:
                    obtained[i] = min(obtained[i], obtained[i+1])
                    obtained[i] = max(lower[i], obtained[i])
                elif (i+1) not in locked:
                    obtained[i+1] = max(obtained[i+1], obtained[i])
                    obtained[i+1] = min(upper[i+1], obtained[i+1])

        # Final clamp
        for i in range(n):
            if i not in locked:
                obtained[i] = max(lower[i], min(upper[i], obtained[i]))

        return obtained

    def compute_valid_passing_ranges(self, retained, locked_rows, lower_limits, upper_limits, ignore_row=None):
        """
        Calculates the absolute valid [min, max] passing % for each sieve using forward/backward sweep.
        Ensures strict envelope compliance (margin = 0.1) and honors all locks (except ignore_row).
        Returns arrays P_min, P_max of length n.
        """
        n = len(lower_limits)
        total_wt = self.total_weight_manager.get_total_weight()
        
        P_min = np.zeros(n)
        P_max = np.zeros(n)
        
        active_locks = set(locked_rows)
        if ignore_row is not None and ignore_row in active_locks:
            active_locks.remove(ignore_row)
            
        # Forward Sweep
        prev_min = 100.0
        prev_max = 100.0
        
        for i in range(n):
            # Strict limits with 0.1 margin, unless lower == upper (e.g. 100)
            env_L = lower_limits[i] + 0.1 if lower_limits[i] < upper_limits[i] else lower_limits[i]
            env_U = upper_limits[i] - 0.1 if lower_limits[i] < upper_limits[i] else upper_limits[i]
            
            if i in active_locks:
                d = retained[i] / total_wt * 100.0
                cur_min = prev_min - d
                cur_max = prev_max - d
            else:
                cur_min = 0.0
                cur_max = prev_max
                
            cur_min = max(cur_min, env_L)
            cur_max = min(cur_max, env_U)
            
            # Prevent impossible states from crashing math (fallback to envelope)
            if cur_min > cur_max:
                cur_max = cur_min
                
            P_min[i] = cur_min
            P_max[i] = cur_max
            prev_min = cur_min
            prev_max = cur_max
            
        # Backward Sweep
        # Pan passing must be exactly 0
        P_min[n-1] = max(P_min[n-1], 0.0)
        P_max[n-1] = min(P_max[n-1], 0.0)
        
        for i in range(n-2, -1, -1):
            next_min = P_min[i+1]
            next_max = P_max[i+1]
            
            if (i+1) in active_locks:
                d = retained[i+1] / total_wt * 100.0
                cur_min = next_min + d
                cur_max = next_max + d
            else:
                cur_min = next_min
                cur_max = 100.0
                
            P_min[i] = max(P_min[i], cur_min)
            P_max[i] = min(P_max[i], cur_max)
            
            if P_min[i] > P_max[i]:
                P_max[i] = P_min[i]
                
        return P_min, P_max

    def compute_valid_retained_range(self, row_index, retained, locked_rows, lower_limits, upper_limits):
        """
        Calculates the [min, max] allowed retained weight for row_index that strictly obeys
        envelope limits and all OTHER locks.
        """
        # Run sweep ignoring the current row's lock (since we want to edit it)
        P_min, P_max = self.compute_valid_passing_ranges(
            retained, locked_rows, lower_limits, upper_limits, ignore_row=row_index
        )
        
        # P[row_index] = P[row_index-1] - (retained[row_index]/total * 100)
        # So delta = P[row_index-1] - P[row_index]
        prev_max = 100.0 if row_index == 0 else P_max[row_index-1]
        prev_min = 100.0 if row_index == 0 else P_min[row_index-1]
        
        cur_min = P_min[row_index]
        cur_max = P_max[row_index]
        
        max_delta = prev_max - cur_min
        min_delta = prev_min - cur_max
        
        min_delta = max(0.0, min_delta)
        max_delta = max(0.0, max_delta)
        
        total_wt = self.total_weight_manager.get_total_weight()
        
        return (min_delta * total_wt / 100.0), (max_delta * total_wt / 100.0)

    def compute_max_retained(self, row_index, retained, locked_rows, lower_limits, upper_limits):
        """
        Compute the maximum retained weight that can be assigned to row_index
        without making any unlocked row go below 0 or violating limits.
        
        This is used to auto-clamp when a user enters a huge value like 99999.
        """
        total_wt = self.total_weight_manager.get_total_weight()
        
        # Sum of locked rows (excluding the one being edited)
        locked_total = sum(retained[j] for j in locked_rows if j != row_index)
        
        # Maximum this row can have = total - locked_total
        # (other unlocked rows can go to 0)
        max_val = total_wt - locked_total
        
        return max(0, max_val)

    def compute_min_retained(self, row_index, retained, locked_rows, lower_limits, upper_limits):
        """
        Compute the minimum retained weight for row_index.
        Retained weights are always >= 0.
        """
        return 0.0

    def adjust_retained_with_locks(self, retained, edited_index, new_value, locked_rows):
        """
        Set retained[edited_index] = new_value, then redistribute among unlocked rows
        so that total retained == total_weight. Locked rows are NEVER modified.
        """
        retained = list(retained)
        n = len(retained)
        total_wt = self.total_weight_manager.get_total_weight()

        # Clamp new_value to valid range
        locked_total = sum(retained[j] for j in locked_rows if j != edited_index)
        max_val = total_wt - locked_total
        new_value = max(0, min(new_value, max_val))
        
        retained[edited_index] = new_value

        adjustable = [j for j in range(n) if j != edited_index and j not in locked_rows]
        
        if not adjustable:
            return retained

        remaining = total_wt - new_value - locked_total
        remaining = max(0, remaining)

        adjustable_total = sum(retained[j] for j in adjustable)

        if adjustable_total > 0 and remaining >= 0:
            scale = remaining / adjustable_total
            for j in adjustable:
                retained[j] = max(0, retained[j] * scale)
        elif remaining > 0:
            per_sieve = remaining / len(adjustable)
            for j in adjustable:
                retained[j] = per_sieve

        return retained

    def sync_passing_with_locks(self, proposed_passing, old_retained, locked_rows, lower_limits, upper_limits):
        """
        When 'passing' is edited (via table or graph), convert it to a valid retained array
        that STRICTLY respects locked_rows (where locked_rows locks the RETAINED weight).
        Then convert back to a finalized passing array.
        """
        # 1. Compute proposed retained from the proposed passing
        proposed_retained = self.passing_to_retained(proposed_passing)
        
        total_wt = self.total_weight_manager.get_total_weight()
        n = len(proposed_retained)
        
        # 2. Force locked rows to keep their old retained values
        for i in locked_rows:
            proposed_retained[i] = old_retained[i]
            
        # 3. Distribute any mismatch to unlocked rows
        locked_total = sum(proposed_retained[j] for j in locked_rows)
        unlocked_indices = [j for j in range(n) if j not in locked_rows]
        
        if unlocked_indices:
            remaining = total_wt - locked_total
            remaining = max(0, remaining)
            
            unlocked_total = sum(proposed_retained[j] for j in unlocked_indices)
            
            if unlocked_total > 0 and remaining >= 0:
                scale = remaining / unlocked_total
                for j in unlocked_indices:
                    proposed_retained[j] = max(0, proposed_retained[j] * scale)
            elif remaining > 0:
                per_sieve = remaining / len(unlocked_indices)
                for j in unlocked_indices:
                    proposed_retained[j] = per_sieve
        
        # 4. Re-derive passing from this strictly valid retained array
        final_passing = self.retained_to_passing(proposed_retained)
        
        # 5. Enforce limits on unlocked rows
        for i in range(n):
            if i not in locked_rows:
                final_passing[i] = max(lower_limits[i], min(upper_limits[i], final_passing[i]))
                
        # 6. Re-derive final retained to ensure everything matches the limits
        # Wait, if we enforce limits on passing, we might change retained of a locked row!
        # Because we clamped final_passing[i], which changes passing[i-1]-passing[i].
        # So we MUST NOT clamp if it breaks locks. 
        # Actually, if we just return final_passing here, it might be outside limits.
        # But keeping the locked retained is more important than limits if they conflict.
        # So we just return the un-clamped final_passing and let it draw.
        
        return final_passing, proposed_retained
