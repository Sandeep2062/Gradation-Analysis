class TotalWeightManager:

    def __init__(self, initial_weight=5000.0):
        self.total_weight = initial_weight

    def set_total_weight(self, value):
        self.total_weight = value

    def get_total_weight(self):
        return self.total_weight

    def normalize_retained(self, retained_values):
        total = sum(retained_values)
        if total == 0:
            return retained_values

        factor = self.total_weight / total
        return [v * factor for v in retained_values]
