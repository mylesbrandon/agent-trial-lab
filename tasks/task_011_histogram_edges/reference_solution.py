import bisect
import math

def _finite_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def histogram_counts(values, edges):
    if len(edges) < 2:
        raise ValueError('at least two edges required')
    if any(not _finite_number(x) for x in (*values, *edges)):
        raise ValueError('finite numeric values and edges required')
    if any(b <= a for a, b in zip(edges, edges[1:])):
        raise ValueError('edges must be strictly increasing')
    counts = [0] * (len(edges) - 1)
    for x in values:
        if edges[0] <= x <= edges[-1]:
            index = min(bisect.bisect_right(edges, x) - 1, len(counts) - 1)
            counts[index] += 1
    return counts
