import math
import pytest
from starter import linear_quantile

def test_extreme_opposite_signs():
    assert linear_quantile([-1e308, 1e308], 0.5) == 0

def test_extreme_same_signs():
    assert linear_quantile([1e308, 1.6e308], 0.5) == _approx(1.3e308)

def test_singleton_and_repeated_values():
    assert linear_quantile((4,), 0.123) == 4
    assert linear_quantile([2, 2, 2], 0.81) == 2

def test_invalid_quantiles():
    for bad in (-0.1, 1.1, math.nan, math.inf, True, '0.5'):
        with pytest.raises(ValueError):
            linear_quantile([1, 2], bad)

def test_invalid_values():
    for bad in (math.inf, math.nan, False, None):
        with pytest.raises(ValueError):
            linear_quantile([1, bad], 0.5)

def test_empty_values():
    with pytest.raises(ValueError):
        linear_quantile([], 0.5)

def test_fractional_rank_and_preservation():
    values = [8, -4, 2, 6, 0]
    assert linear_quantile(values, 0.4) == _approx(1.2)
    assert values == [8, -4, 2, 6, 0]


def test_integer_outside_float_range():
    with pytest.raises(ValueError):
        linear_quantile([10**1000], 0.5)


def _approx(value, *, rel=1e-12, abs=1e-12):
    return pytest.approx(value, rel=rel, abs=abs)


def test_large_integer_interpolation_keeps_small_result():
    assert linear_quantile([-10**20, 10**20 + 1], 0.5) == _approx(0.5)
