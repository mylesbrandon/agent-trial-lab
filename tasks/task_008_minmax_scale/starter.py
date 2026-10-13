def minmax_scale(values):
    low, high = min(values), max(values)
    return [(x - low) / (high - low) for x in values]
