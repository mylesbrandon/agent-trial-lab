import pytest
from starter import aggregate_payments_csv


def test_basic_totals():
    assert aggregate_payments_csv("group,amount\na,1.20\na,2.3\nb,4\n") == [
        {"group": "a", "total": "3.50", "count": 2}, {"group": "b", "total": "4.00", "count": 1}]


def test_empty_and_header_only():
    assert aggregate_payments_csv("") == []
    assert aggregate_payments_csv("group,amount\n") == []


def test_invalid_amount():
    with pytest.raises(ValueError):
        aggregate_payments_csv("group,amount\na,hello\n")
