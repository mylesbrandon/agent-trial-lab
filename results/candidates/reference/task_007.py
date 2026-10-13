import math
from fractions import Fraction

def _finite_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def linear_quantile(values, q):
    if not values:
        raise ValueError('values must be nonempty')
    for x in (*values, q):
        if not _finite_number(x):
            raise ValueError('finite numeric values required')
    if not 0 <= q <= 1:
        raise ValueError('q must be in [0, 1]')
    ordered = sorted(values)
    h = (len(ordered) - 1) * q
    low = math.floor(h)
    high = math.ceil(h)
    fraction = Fraction(h - low)
    return float((1 - fraction) * Fraction(ordered[low]) + fraction * Fraction(ordered[high]))
