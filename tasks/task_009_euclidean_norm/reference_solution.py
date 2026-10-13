import math

def _finite_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def euclidean_norm(values):
    if any(not _finite_number(x) for x in values):
        raise ValueError('finite numeric values required')
    return math.hypot(*values)
