import math
from fractions import Fraction

def _finite_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def merge_moments(left, right):
    for item in (left, right):
        if not isinstance(item, tuple) or len(item) != 3:
            raise ValueError('summary must be a three-item tuple')
        n, mean, m2 = item
        if isinstance(n, bool) or not isinstance(n, int) or n < 0:
            raise ValueError('count must be a nonnegative integer')
        if any(not _finite_number(x) for x in (mean, m2)):
            raise ValueError('finite numeric moments required')
        if m2 < 0 or (n == 0 and (mean != 0 or m2 != 0)):
            raise ValueError('invalid empty summary or negative m2')
    a, ma, sa = left
    b, mb, sb = right
    if a == 0:
        return (b, mb, sb) if b else (0, 0.0, 0.0)
    if b == 0:
        return left
    delta = Fraction(mb) - Fraction(ma)
    n = a + b
    mean = Fraction(ma) + delta * b / n
    m2 = Fraction(sa) + Fraction(sb) + delta * delta * a * b / n
    return n, float(mean), float(m2)
