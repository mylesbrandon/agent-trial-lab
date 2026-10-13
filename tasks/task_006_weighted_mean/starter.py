def weighted_mean(values, weights):
    return sum(v * w for v, w in zip(values, weights)) / sum(weights)
