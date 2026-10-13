import pytest
from starter import drawdown_durations


def test_strictly_increasing_values_have_no_drawdowns():
    assert drawdown_durations([0, 1, 2], [1, 2, 3]) == [0, 0, 0]


def test_dip_then_new_high_resets_clock():
    assert drawdown_durations([0, 2, 5, 7], [10, 8, 12, 11]) == [0, 2, 0, 2]


def test_duration_uses_irregular_elapsed_time():
    assert drawdown_durations([0, 3, 9], [10, 8, 9]) == [0, 3, 9]


def test_empty_inputs():
    assert drawdown_durations([], []) == []
