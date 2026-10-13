import pytest
from starter import linear_quantile

def test_median_of_odd_input():
    assert linear_quantile([7, 1, 3], 0.5) == 3

def test_endpoints():
    assert linear_quantile([4, 1, 9], 0) == 1
    assert linear_quantile([4, 1, 9], 1) == 9

def test_interpolated_quartile():
    assert linear_quantile([0, 10, 20, 30], 0.25) == _approx(7.5)


def _approx(value, *, rel=1e-12, abs=1e-12):
    return pytest.approx(value, rel=rel, abs=abs)
