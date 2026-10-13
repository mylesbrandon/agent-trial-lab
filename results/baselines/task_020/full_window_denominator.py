# Deliberately flawed diagnostic baseline; not a model result.
import math


def time_weighted_mean(times, values, queries, window):
    if len(times) != len(values):
        raise ValueError("times and values must have equal length")
    if any(type(t) is not int or abs(t) > 10**12 for t in (*times, *queries)):
        raise ValueError("timestamps must be integers")
    if any(a >= b for a, b in zip(times, times[1:])):
        raise ValueError("observation times must be strictly increasing")
    if type(window) is not int or not 0 < window <= 10**12:
        raise ValueError("window must be a positive integer")
    if any(
        type(v) not in (int, float)
        or (type(v) is float and not math.isfinite(v))
        or abs(v) > 10**12
        for v in values
    ):
        raise ValueError("values must be finite numbers")
    result = []
    for query in queries:
        if not times or query <= times[0]:
            result.append(None)
            continue
        start = query - window
        covered = window
        areas = []
        for index, timestamp in enumerate(times):
            if timestamp >= query:
                break
            next_time = times[index + 1] if index + 1 < len(times) else query
            left, right = max(timestamp, start), min(next_time, query)
            if right > left:
                areas.append(values[index] * (right - left))
        result.append(math.fsum(areas) / covered)
    return result
