import pytest
from starter import resample_ohlc


def test_ordinary_bins():
    assert resample_ohlc([0, 2, 5], [10, 12, 7], 5) == [
        (0, 10, 12, 10, 12), (5, 7, 7, 7, 7)
    ]


def test_empty_inputs():
    assert resample_ohlc([], [], 5) == []


def test_one_observation_sets_all_prices():
    assert resample_ohlc([8], [3], 5) == [(5, 3, 3, 3, 3)]


def test_zero_width_is_invalid():
    with pytest.raises(ValueError):
        resample_ohlc([0], [1], 0)
