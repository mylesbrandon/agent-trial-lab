import pytest
from starter import deduplicate_csv


def test_unique_records():
    assert deduplicate_csv("id,x\na,1\nb,2\n", ["id"]) == [{"id": "a", "x": "1"}, {"id": "b", "x": "2"}]


def test_first_and_last_policy():
    text = "id,x\na,1\na,2\n"
    assert deduplicate_csv(text, ["id"], "first") == [{"id": "a", "x": "1"}]
    assert deduplicate_csv(text, ["id"]) == [{"id": "a", "x": "2"}]


def test_empty_and_bad_policy():
    assert deduplicate_csv("", ["id"]) == []
    with pytest.raises(ValueError):
        deduplicate_csv("", ["id"], "any")
