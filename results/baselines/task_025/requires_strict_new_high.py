# Deliberately flawed diagnostic baseline; not a model result.
import math


def drawdown_durations(times, values):
    if len(times) != len(values):
        raise ValueError("times and values must have equal length")
    if any(type(t) is not int for t in times):
        raise ValueError("timestamps must be integers")
    if any(a >= b for a, b in zip(times, times[1:])):
        raise ValueError("times must be strictly increasing")
    if any(
        type(v) not in (int, float)
        or (type(v) is float and not math.isfinite(v))
        or v <= 0
        for v in values
    ):
        raise ValueError("values must be positive finite numbers")
    if not times:
        return []
    peak, recovered_at = values[0], times[0]
    durations = []
    for timestamp, value in zip(times, values):
        if value > peak:
            peak, recovered_at = value, timestamp
        durations.append(timestamp - recovered_at)
    return durations
