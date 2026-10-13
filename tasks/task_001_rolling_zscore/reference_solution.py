import math
def rolling_zscore(values, window):
    if window <=0:
        raise ValueError("window must be positive")

    result = []

    for i, current in enumerate(values):
        # If the current value is NaN, output NaN.
        if math.isnan(current):
            result.append(float("nan"))
            continue

        # Select rolling window ending at current index.
        start = max(0,i-window+1)
        window_values = values[start:i+1]

        # Ignore NaNs inside the window.
        valid_values = [x for x in window_values if not math.isnan(x)]

        # This case mostly matter if current is NaN, but keep it for safety.
        if len(valid_values) == 0:
            result.append(float("nan"))
            continue

        mean = sum(valid_values) / len(valid_values)

        variance = sum((x - mean) ** 2 for x in valid_values) / len (valid_values)
        std = math.sqrt(variance)

        if std == 0:
            result.append(0.0)
        else:
            z = (current - mean) / std
            result.append(z)
    return result
