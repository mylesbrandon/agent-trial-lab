# Deliberately flawed diagnostic baseline; not a model result.
import math


def resample_ohlc(times, prices, width, origin=0):
    if len(times) != len(prices):
        raise ValueError("times and prices must have equal length")
    if type(width) is not int or width <= 0 or type(origin) is not int:
        raise ValueError("width must be positive integer; origin must be integer")
    if any(type(t) is not int for t in times):
        raise ValueError("timestamps must be integers")
    if any(a > b for a, b in zip(times, times[1:])):
        raise ValueError("times must be nondecreasing")
    if any(
        type(p) not in (int, float) or (type(p) is float and not math.isfinite(p))
        for p in prices
    ):
        raise ValueError("prices must be finite numbers")
    result = []
    for timestamp, price in zip(times, prices):
        start = origin + int((timestamp - origin) / width) * width
        if not result or result[-1][0] != start:
            result.append((start, price, price, price, price))
        else:
            start, opening, high, low, _ = result[-1]
            result[-1] = (start, opening, max(high, price), min(low, price), price)
    return result
