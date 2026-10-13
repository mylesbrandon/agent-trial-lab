import pytest
from starter import parse_csv_schema


def test_canonical_header():
    assert parse_csv_schema("id,name\n1,Ada\n", ["id", "name"]) == [{"id": "1", "name": "Ada"}]


def test_reordered_normalized_header():
    assert parse_csv_schema(" NAME , ID \n Ada , 1 \n", ["id", "name"]) == [{"id": "1", "name": "Ada"}]


def test_empty_input_and_missing_column():
    assert parse_csv_schema("  \n", ["id"]) == []
    with pytest.raises(ValueError):
        parse_csv_schema("id\n1\n", ["id", "name"])
