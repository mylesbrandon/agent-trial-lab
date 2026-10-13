import math
import pytest
from starter import weighted_mean

def test_large_weight_sum():
    assert weighted_mean([2, 4], [1e308, 1e308]) == _approx(3)

def test_large_products_and_cancellation():
    assert weighted_mean([1e308, -1e308], [2, 2]) == 0
    assert weighted_mean([1e308, 1e308], [2, 2]) == _approx(1e308)

def test_negative_or_all_zero_weights():
    for weights in ([1, -1], [0, 0]):
        with pytest.raises(ValueError):
            weighted_mean([1, 2], weights)

def test_empty_and_mismatched_lengths():
    for values, weights in (([], []), ([1], []), ([1], [1, 2])):
        with pytest.raises(ValueError):
            weighted_mean(values, weights)

def test_invalid_values_even_with_zero_weight():
    for bad in (True, math.inf, math.nan, '3'):
        with pytest.raises(ValueError):
            weighted_mean([bad, 2], [0, 1])

def test_invalid_weights():
    for bad in (True, math.inf, math.nan, '3'):
        with pytest.raises(ValueError):
            weighted_mean([1, 2], [1, bad])

def test_zero_and_tuple_inputs():
    assert weighted_mean((0, 0), (1, 2)) == 0

def test_input_preservation():
    values, weights = [5, 1], [2, 1]
    assert weighted_mean(values, weights) == _approx(11 / 3)
    assert values == [5, 1] and weights == [2, 1]


def test_integer_outside_float_range():
    with pytest.raises(ValueError):
        weighted_mean([10**1000], [1])


def _approx(value, *, rel=1e-12, abs=1e-12):
    return pytest.approx(value, rel=rel, abs=abs)


def test_large_integer_cancellation_keeps_small_mean():
    assert weighted_mean([10**20 + 1, -10**20], [1, 1]) == _approx(0.5)


def test_nearby_large_float_cancellation():
    values = [1e308, -math.nextafter(1e308, 0.0)]
    assert weighted_mean(values, [1, 1]) == _approx((values[0] + values[1]) / 2)
