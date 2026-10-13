import math


def bounded_forward_fill(times, values, max_gap):
    if len(times) != len(values):
        raise ValueError("times and values must have equal length")
    if type(max_gap) is not int or max_gap < 0:
        raise ValueError("max_gap must be a nonnegative integer")
    if any(type(t) is not int for t in times):
        raise ValueError("timestamps must be integers")
    if any(a >= b for a, b in zip(times, times[1:])):
        raise ValueError("times must be strictly increasing")
    if any(
        v is not None and (
            type(v) not in (int, float)
            or (type(v) is float and not math.isfinite(v))
        )
        for v in values
    ):
        raise ValueError("values must be finite numbers or None")
    last_time, last_value = None, None
    result = []
    for timestamp, value in zip(times, values):
        if value is not None:
            last_time, last_value = timestamp, value
            result.append(value)
        elif last_time is not None and timestamp - last_time <= max_gap:
            result.append(last_value)
        else:
            result.append(None)
    return result
