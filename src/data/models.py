class Material:
    def __init__(self, name):
        self.name = name
        self.sieve_sizes = []
        self.lower_limits = []
        self.upper_limits = []
        self.passing = []

class FineAggregate(Material):
    def __init__(self):
        super().__init__("Fine Aggregate")
        # Default values will be set when loading data
        self.sheet_name = "Gradation analysis"
        self.sieve_range = "A20:A27"
        self.weight_retained_range = "B20:B27"
        self.passing_range = "F20:F27"
        self.lower_limit_range = "G20:G27"
        self.upper_limit_range = "H20:H27"
        self.total_weight_cell = "E17"

class SubBase(Material):
    def __init__(self):
        super().__init__("Sub-Base")
        # Default values will be set when loading data
        self.sheet_name = "Gradation"
        self.sieve_range = "A18:A26"
        self.weight_retained_range = "B18:B26"
        self.passing_range = "F18:F26"
        self.lower_limit_range = "G18:G26"
        self.upper_limit_range = "H18:H26"
        self.total_weight_cell = "B27"