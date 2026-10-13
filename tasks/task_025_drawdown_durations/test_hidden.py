import pytest
from starter import drawdown_durations


def test_equal_high_recovers_and_resets_clock():
    assert drawdown_durations([0, 2, 7, 8, 10], [10, 8, 9, 10, 7]) == [0, 2, 7, 0, 2]


def test_peak_plateau_uses_most_recent_peak_timestamp():
    assert drawdown_durations([0, 5, 8], [10, 10, 9]) == [0, 0, 3]


def test_local_high_below_global_peak_does_not_reset_clock():
    assert drawdown_durations([1, 3, 6, 10], [20, 5, 10, 15]) == [0, 2, 5, 9]


def test_new_global_peak_replaces_previous_reference():
    assert drawdown_durations([0, 1, 4, 9, 11], [5, 4, 6, 5, 6]) == [0, 1, 0, 5, 0]


def test_near_equal_value_is_still_below_peak():
    assert drawdown_durations([0, 10], [1.0, 0.999999999999]) == [0, 10]


def test_invalid_values_raise():
    for value in [0, -1, True, None, "2", float("nan"), float("inf")]:
        with pytest.raises(ValueError):
            drawdown_durations([0], [value])


def test_invalid_times_or_lengths_raise():
    for times, values in [([0, 0], [1, 2]), ([2, 1], [1, 2]),
                          ([True], [1]), ([1.5], [1]), ([1], [])]:
        with pytest.raises(ValueError):
            drawdown_durations(times, values)


def test_negative_times_tuples_and_no_mutation():
    times, values = [-5, -2, 1], [4, 3, 2]
    assert drawdown_durations(times, values) == [0, 3, 6]
    assert (times, values) == ([-5, -2, 1], [4, 3, 2])
    assert drawdown_durations(tuple(times), tuple(values)) == [0, 3, 6]
