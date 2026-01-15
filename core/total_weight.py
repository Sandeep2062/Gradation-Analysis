class TotalWeightManager:

    def __init__(self):
        self.total_weight = 2000.0

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
