import math
from fractions import Fraction

def stable_softmax(scores):
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) for x in scores):
        raise ValueError('scores must be numbers other than NaN')
    try:
        converted = [float(x) for x in scores]
    except OverflowError as error:
        raise ValueError('integer score exceeds float range') from error
    if any(math.isnan(x) for x in converted):
        raise ValueError('NaN is not a score')
    if not scores:
        return []
    positive = sum(x == math.inf for x in scores)
    if positive:
        return [1.0 / positive if x == math.inf else 0.0 for x in scores]
    maximum = max(scores)
    if maximum == -math.inf:
        return [1.0 / len(scores)] * len(scores)
    # Preserve accepted integer distinctions before converting the exponent.
    exponents = []
    for score in scores:
        if score == -math.inf:
            exponents.append(0.0)
            continue
        delta = Fraction(score) - Fraction(maximum)
        exponents.append(math.exp(float(delta)) if delta >= -746 else 0.0)
    total = math.fsum(exponents)
    return [x / total for x in exponents]
