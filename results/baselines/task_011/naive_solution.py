def histogram_counts(values, edges):
    return [sum(a <= x < b for x in values) for a, b in zip(edges, edges[1:])]
