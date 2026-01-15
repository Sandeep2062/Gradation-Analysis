fine_aggregate = {
    "sieve_range": range(20, 28),
    "sieve_column": "A",
    "weight_column": "B",
    "passing_column": "F",
    "lower_column": "G",
    "upper_column": "H",
    "total_weight_cell": "E17",
    "sieve_sizes": [10.00, 4.75, 2.36, 1.18, 0.60, 0.30, 0.15, "Pan"],
    "lower_limits": [100.00, 90.00, 75.00, 55.00, 35.00, 8.00, 0.00, 0.00],
    "upper_limits": [100.00, 100.00, 100.00, 90.00, 59.00, 30.00, 10.00, 0.00],
}

coarse_aggregate = {
    "sieve_range": range(18, 22),
    "sieve_column": "A",
    "weight_column": "B",
    "passing_column": "F",
    "lower_column": "G",
    "upper_column": "H",
    "total_weight_cell": "B27",
    "sieve_sizes": [40.00, 20.00, 10.00, 4.75, "Pan"],
    "lower_limits": [100.00, 90.00, 25.00, 0.00, 0.00],
    "upper_limits": [100.00, 100.00, 35.00, 10.00, 0.00],
}

sub_base = {
    "sieve_range": range(18, 27),
    "sieve_column": "A",
    "weight_column": "B",
    "passing_column": "F",
    "lower_column": "G",
    "upper_column": "H",
    "total_weight_cell": "B27",
    "sieve_sizes": [75.00, 53.00, 26.50, 9.50, 4.750, 2.360, 0.425, 0.075, "Pan"],
    "lower_limits": [100.00, 80.00, 55.00, 35.00, 25.00, 20.00, 10.00, 0.00, 0.00],
    "upper_limits": [100.00, 100.00, 90.00, 65.00, 55.00, 40.00, 15.00, 5.00, 0.00],
}

crm_base = {
    "sieve_range": range(18, 27),
    "sieve_column": "A",
    "weight_column": "B",
    "passing_column": "F",
    "lower_column": "G",
    "upper_column": "H",
    "total_weight_cell": "B27",
    "sieve_sizes": [45.00, 22.40, 5.60, 0.710, 0.09, "Pan"],
    "lower_limits": [100.00, 90.00, 35.00, 10.00, 2.00, 0.00],
    "upper_limits": [100.00, 100.00, 55.00, 30.00, 5.00, 0.00],
}

materials = {
    "fine": fine_aggregate,
    "coarse": coarse_aggregate,
    "subbase": sub_base,
    "crm": crm_base
}
