import pytest
from starter import aggregate_payments_csv


def test_exact_large_cancellation_and_cents():
    text = "group,amount\na,9007199254740993.01\na,-9007199254740993.00\na,0.10\na,0.20\n"
    assert aggregate_payments_csv(text) == [{"group": "a", "total": "0.31", "count": 4}]


def test_missing_values_create_groups_without_counts():
    assert aggregate_payments_csv("group,amount\nb,\na,1\nb, \nc,\n") == [
        {"group": "b", "total": "0.00", "count": 0}, {"group": "a", "total": "1.00", "count": 1},
        {"group": "c", "total": "0.00", "count": 0}]


def test_signed_values_canonical_zero_and_leading_zeroes():
    assert aggregate_payments_csv("group,amount\na,-0.00\na,+0002.5\na,-2.50\nb,-0.01\n") == [
        {"group": "a", "total": "0.00", "count": 3}, {"group": "b", "total": "-0.01", "count": 1}]


def test_strict_decimal_grammar():
    for amount in ("1e2", "NaN", "inf", "1.001", ".50", "1.", "１２", "--1"):
        with pytest.raises(ValueError):
            aggregate_payments_csv(f"group,amount\na,{amount}\n")


def test_quoted_groups_normalization_and_case():
    assert aggregate_payments_csv('group,amount\n" x,y ", 1 \n"line\nnext",2\nA,3\na,4\n') == [
        {"group": "x,y", "total": "1.00", "count": 1}, {"group": "line\nnext", "total": "2.00", "count": 1},
        {"group": "A", "total": "3.00", "count": 1}, {"group": "a", "total": "4.00", "count": 1}]


def test_bad_headers_rows_and_groups():
    for text in ("amount,group\n1,a\n", "group,amount\na\n", "group,amount\na,1,2\n", "group,amount\n ,1\n", 'group,amount\n"a,1'):
        with pytest.raises(ValueError):
            aggregate_payments_csv(text)


def test_blank_rows_and_first_appearance_order():
    assert aggregate_payments_csv(" group , amount \n\nb,1\na,2\nb,3\n") == [
        {"group": "b", "total": "4.00", "count": 2}, {"group": "a", "total": "2.00", "count": 1}]
