import pytest
from starter import merge_moments

def test_equal_group_means():
    assert merge_moments((2, 3, 2), (2, 3, 8)) == _approx((4, 3, 10))

def test_distinct_singletons():
    assert merge_moments((1, 1, 0), (1, 3, 0)) == _approx((2, 2, 2))

def test_weighted_group_means():
    assert merge_moments((1, 0, 0), (3, 4, 2)) == _approx((4, 3, 14))


def _approx(value, *, rel=1e-10, abs=1e-10):
    return pytest.approx(value, rel=rel, abs=abs)
