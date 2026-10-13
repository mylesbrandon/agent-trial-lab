import pytest
from starter import time_weighted_mean


def test_irregular_durations_determine_weights():
    assert time_weighted_mean([0, 2], [10, 20], [5], 5) == pytest.approx([16])


def test_constant_signal():
    assert time_weighted_mean([0, 4, 8], [3, 3, 3], [4, 8, 12], 4) == pytest.approx([3, 3, 3])


def test_queries_before_first_observation_have_no_mean():
    assert time_weighted_mean([4], [9], [0, 4], 3) == [None, None]
    assert time_weighted_mean([], [], [1, 2], 3) == [None, None]


def test_invalid_window_raises():
    with pytest.raises(ValueError):
        time_weighted_mean([0], [1], [2], 0)
