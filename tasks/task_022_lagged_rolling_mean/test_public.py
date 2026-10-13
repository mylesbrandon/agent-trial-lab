import pytest
from starter import lagged_rolling_mean


def test_regular_rolling_mean_uses_previous_rows():
    assert lagged_rolling_mean([10, 20, 30, 40], 2) == [None, 10, 15, 25]


def test_missing_observations_are_ignored():
    assert lagged_rolling_mean([None, 8, None, 4], 2) == [None, None, 8, 8]


def test_minimum_valid_observation_count():
    assert lagged_rolling_mean([1, 2, 3, 4], 3, min_periods=2) == [None, None, 1.5, 2]


def test_empty_input_returns_empty_list():
    assert lagged_rolling_mean([], 3) == []
