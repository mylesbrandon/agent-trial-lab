import pytest
from starter import bounded_forward_fill


def test_fill_within_age_limit():
    assert bounded_forward_fill([0, 2, 4], [7, None, 8], 2) == [7, 7, 8]


def test_leading_missing_values_remain_missing():
    assert bounded_forward_fill([0, 1, 2], [None, None, 9], 5) == [None, None, 9]


def test_zero_is_an_observed_value():
    assert bounded_forward_fill([0, 1], [0, None], 2) == [0, 0]


def test_empty_input():
    assert bounded_forward_fill([], [], 2) == []
