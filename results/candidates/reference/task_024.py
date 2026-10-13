def purged_time_split(intervals, test_start, test_end, embargo=0):
    if not isinstance(intervals, (list, tuple)):
        raise ValueError("intervals must be a list or tuple")
    if any(type(x) is not int for x in (test_start, test_end, embargo)):
        raise ValueError("split bounds and embargo must be integers")
    if test_start >= test_end or embargo < 0:
        raise ValueError("invalid split bounds or embargo")
    for interval in intervals:
        if not isinstance(interval, (list, tuple)) or len(interval) != 2:
            raise ValueError("each interval must be an endpoint pair")
        start, end = interval
        if type(start) is not int or type(end) is not int or start >= end:
            raise ValueError("intervals require integer start < end")
    test = [
        i for i, (start, _) in enumerate(intervals)
        if test_start <= start < test_end
    ]
    protected_end = max([test_end] + [intervals[i][1] for i in test]) + embargo
    test_set = set(test)
    train = [
        i for i, (start, end) in enumerate(intervals)
        if i not in test_set and (end <= test_start or start >= protected_end)
    ]
    return train, test
