import pytest
from starter import resample_ohlc


def test_boundary_belongs_to_next_bin():
    assert resample_ohlc([4, 5, 9, 10], [1, 3, 2, 4], 5) == [
        (0, 1, 1, 1, 1), (5, 3, 3, 2, 2), (10, 4, 4, 4, 4)
    ]


def test_negative_offsets_use_floor_division():
    assert resample_ohlc([-4, -3, 1, 2], [4, 3, 1, 2], 5, origin=2) == [
        (-8, 4, 4, 4, 4), (-3, 3, 3, 1, 1), (2, 2, 2, 2, 2)
    ]


def test_duplicate_timestamps_preserve_open_and_close_order():
    assert resample_ohlc([1, 1, 1], [8, 2, 5], 10) == [(0, 8, 8, 2, 5)]


def test_empty_bins_are_omitted_and_negative_prices_work():
    assert resample_ohlc([0, 100], [-2, 0], 10) == [(0, -2, -2, -2, -2), (100, 0, 0, 0, 0)]


def test_nonfinite_or_nonnumeric_prices_raise():
    for price in [None, True, "3", float("nan"), float("inf"), -float("inf")]:
        with pytest.raises(ValueError):
            resample_ohlc([0], [price], 1)


def test_invalid_times_and_mismatched_lengths_raise():
    for times, prices in [([2, 1], [1, 2]), ([True], [1]), ([1.0], [1]), ([1], [])]:
        with pytest.raises(ValueError):
            resample_ohlc(times, prices, 1)


def test_parameter_validation_occurs_for_empty_inputs():
    for width, origin in [(True, 0), (-1, 0), (1.5, 0), (1, True), (1, 0.5)]:
        with pytest.raises(ValueError):
            resample_ohlc([], [], width, origin)


def test_tuple_inputs_and_no_mutation():
    times, prices = [0, 2, 2], [3, 1, 4]
    expected = [(0, 3, 4, 1, 4)]
    assert resample_ohlc(times, prices, 3) == expected
    assert (times, prices) == ([0, 2, 2], [3, 1, 4])
    assert resample_ohlc(tuple(times), tuple(prices), 3) == expected
