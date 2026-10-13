import pytest
from starter import lagged_rolling_mean


def test_current_spike_cannot_affect_current_feature():
    assert lagged_rolling_mean([2, 2, 1000], 2) == [None, 2, 2]


def test_missing_rows_still_consume_window_positions():
    assert lagged_rolling_mean([9, None, None, 4], 2) == [None, 9, 9, None]


def test_min_periods_counts_nonmissing_values_only():
    assert lagged_rolling_mean([1, None, 5, None, 9], 3, 2) == [None, None, None, 3, None]


def test_zero_values_are_observations():
    assert lagged_rolling_mean([0, 0, 10], 2, 2) == [None, None, 0]


def test_window_longer_than_series_uses_available_history():
    assert lagged_rolling_mean([2, -4, 8], 20) == [None, 2, -1]


def test_invalid_values_are_rejected_even_in_final_row():
    for value in [True, "1", float("nan"), float("inf"), -float("inf")]:
        with pytest.raises(ValueError):
            lagged_rolling_mean([1, value], 1)


def test_parameters_are_validated_for_empty_input():
    for window, minimum in [(0, 1), (-1, 1), (True, 1), (1.5, 1),
                            (2, 0), (2, 3), (2, True), (2, 1.5)]:
        with pytest.raises(ValueError):
            lagged_rolling_mean([], window, minimum)


def test_tuple_input_and_no_mutation():
    values = [1.5, None, -2.5, 9]
    expected = [None, 1.5, 1.5, -2.5]
    assert lagged_rolling_mean(values, 2) == expected
    assert values == [1.5, None, -2.5, 9]
    assert lagged_rolling_mean(tuple(values), 2) == expected


def test_supported_magnitude_bound_is_inclusive():
    bound = 10**12
    assert lagged_rolling_mean([bound, -bound, 0], 2) == [None, bound, 0]
    for invalid in [bound + 1, -bound - 1, 10**400]:
        with pytest.raises(ValueError):
            lagged_rolling_mean([invalid], 2)
