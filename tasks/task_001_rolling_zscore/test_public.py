import math
from starter import rolling_zscore
import pytest

def test_invalid_window():
    with pytest.raises(ValueError):
        rolling_zscore([1, 2, 3], 0)

def almost_equal(a, b, tol=1e-6):
    if math.isnan(a) and math.isnan(b):
        return True
    return abs(a - b) < tol

def test_basic_increasing_sequence():
    result = rolling_zscore([1, 2, 3], 2)
    assert len(result) == 3
    assert almost_equal(result[0], 0.0)
    assert almost_equal(result[1], 1.0)
    assert almost_equal(result[2], 1.0)

def test_window_size_three():
    result = rolling_zscore([1, 2, 3, 4], 3)

    assert len(result) == 4
    assert almost_equal(result[0], 0.0)
