# Deliberately flawed diagnostic baseline; not a model result.
from bisect import bisect_left, bisect_right


def backward_asof(query_times, observation_times, values, max_age=None, allow_exact=True):
    if len(observation_times) != len(values):
        raise ValueError("observation times and values must have equal length")
    if any(type(t) is not int for t in (*query_times, *observation_times)):
        raise ValueError("timestamps must be integers")
    if any(a > b for a, b in zip(observation_times, observation_times[1:])):
        raise ValueError("observation times must be nondecreasing")
    if max_age is not None and (type(max_age) is not int or max_age < 0):
        raise ValueError("max_age must be a nonnegative integer or None")
    if type(allow_exact) is not bool:
        raise ValueError("allow_exact must be bool")
    search = bisect_right
    result = []
    for query in query_times:
        index = search(observation_times, query) - 1
        if index < 0 or (
            max_age is not None and query - observation_times[index] > max_age
        ):
            result.append(None)
        else:
            result.append(values[index])
    return result
