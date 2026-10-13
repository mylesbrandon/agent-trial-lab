def linear_quantile(values, q):
    values = sorted(values)
    return values[int((len(values) - 1) * q)]
