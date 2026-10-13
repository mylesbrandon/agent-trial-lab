import pytest
from starter import bounded_forward_fill


def test_filled_rows_do_not_refresh_source_age():
    assert bounded_forward_fill([0, 2, 4, 6], [7, None, None, None], 4) == [7, 7, 7, None]


def test_gap_measures_elapsed_time_not_number_of_rows():
    assert bounded_forward_fill([0, 100], [4, None], 2) == [4, None]


def test_fresh_observation_restores_filling_after_expiry():
    assert bounded_forward_fill([0, 5, 6, 7], [1, None, -3, None], 1) == [1, None, -3, -3]


def test_zero_gap_does_not_fill_later_missing_rows():
    assert bounded_forward_fill([0, 1, 2], [8, None, 9], 0) == [8, None, 9]


def test_negative_timestamps_have_inclusive_age_boundary():
    assert bounded_forward_fill([-5, -2, -1], [6, None, None], 3) == [6, 6, None]


def test_invalid_times_and_lengths_raise():
    for times, values in [([0, 0], [1, None]), ([2, 1], [1, None]),
                          ([True], [1]), ([1.0], [1]), ([0], [])]:
        with pytest.raises(ValueError):
            bounded_forward_fill(times, values, 3)


def test_invalid_values_and_gap_raise():
    for value in [True, "1", float("nan"), float("inf")]:
        with pytest.raises(ValueError):
            bounded_forward_fill([0], [value], 1)
    for gap in [-1, True, 0.5]:
        with pytest.raises(ValueError):
            bounded_forward_fill([], [], gap)


def test_no_mutation_and_tuple_inputs():
    times, values = [0, 1, 2], [None, 2.5, None]
    assert bounded_forward_fill(times, values, 1) == [None, 2.5, 2.5]
    assert (times, values) == ([0, 1, 2], [None, 2.5, None])
    assert bounded_forward_fill(tuple(times), tuple(values), 1) == [None, 2.5, 2.5]
