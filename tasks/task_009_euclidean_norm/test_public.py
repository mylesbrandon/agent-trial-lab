import pytest
from starter import euclidean_norm

def test_pythagorean_triple():
    assert euclidean_norm([3, 4]) == _approx(5)

def test_sign_invariance():
    assert euclidean_norm([-3, 4, -12]) == _approx(13)

def test_empty_norm():
    assert euclidean_norm([]) == 0


def _approx(value, *, rel=1e-12, abs=1e-12):
    return pytest.approx(value, rel=rel, abs=abs)
