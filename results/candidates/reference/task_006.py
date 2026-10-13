import math
from fractions import Fraction

def _finite_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def weighted_mean(values, weights):
    if not values or len(values) != len(weights):
        raise ValueError('nonempty equally sized inputs required')
    for x in (*values, *weights):
        if not _finite_number(x):
            raise ValueError('finite numeric inputs required')
    if any(w < 0 for w in weights) or not any(w > 0 for w in weights):
        raise ValueError('nonnegative weights with positive total required')
    # Exact rational arithmetic provides an independent oracle without
    # overflow or cancellation from scaling large, nearly equal integers.
    total = sum(Fraction(w) for w in weights)
    numerator = sum(Fraction(v) * Fraction(w) for v, w in zip(values, weights))
    return float(numerator / total)
