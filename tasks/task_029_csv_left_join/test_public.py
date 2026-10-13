import pytest
from starter import left_join_csv


def test_matched_and_unmatched_rows():
    assert left_join_csv("id,value\na,1\nb,2\n", "id,label\na,Alpha\n") == [
        {"id": "a", "value": "1", "label": "Alpha"}, {"id": "b", "value": "2", "label": None}]


def test_empty_tables():
    assert left_join_csv("", "") == []
    assert left_join_csv("id,value\na,1\n", "") == [{"id": "a", "value": "1", "label": None}]


def test_wrong_header():
    with pytest.raises(ValueError):
        left_join_csv("id,label\na,1\n", "")
