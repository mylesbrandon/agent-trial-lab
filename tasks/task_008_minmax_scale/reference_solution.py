import math
from fractions import Fraction

def _finite_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def minmax_scale(values):
    if any(not _finite_number(x) for x in values):
        raise ValueError('finite numeric values required')
    if not values:
        return []
    values = [Fraction(x) for x in values]
    low, high = min(values), max(values)
    if low == high:
        return [0.0] * len(values)
    span = high - low
    return [float((x - low) / span) for x in values]
