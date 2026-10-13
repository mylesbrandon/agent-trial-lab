import math


def lagged_rolling_mean(values, window, min_periods=1):
    if type(window) is not int or window <= 0:
        raise ValueError("window must be a positive integer")
    if type(min_periods) is not int or not 1 <= min_periods <= window:
        raise ValueError("min_periods must be between 1 and window")
    if any(
        v is not None and (
            type(v) not in (int, float)
            or (type(v) is float and not math.isfinite(v))
            or abs(v) > 10**12
        )
        for v in values
    ):
        raise ValueError("values must be finite numbers or None")
    result = []
    for index in range(len(values)):
        sample = [v for v in values[max(0, index - window):index] if v is not None]
        result.append(math.fsum(sample) / len(sample) if len(sample) >= min_periods else None)
    return result
