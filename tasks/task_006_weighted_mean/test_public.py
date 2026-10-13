import pytest
from starter import weighted_mean

def test_ordinary_weights():
    assert weighted_mean([10, 20, 30], [1, 2, 1]) == _approx(20)

def test_unequal_weights():
    assert weighted_mean([0, 10], [1, 3]) == _approx(7.5)

def test_zero_weight():
    assert weighted_mean([99, -2], [0, 1]) == -2


def _approx(value, *, rel=1e-12, abs=1e-12):
    return pytest.approx(value, rel=rel, abs=abs)
