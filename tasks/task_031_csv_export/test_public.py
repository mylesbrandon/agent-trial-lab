import pytest
from starter import export_records_csv


def test_basic_serialization_and_column_order():
    assert export_records_csv([{"id": 1, "name": "Ada"}], ["name", "id"]) == "name,id\r\nAda,1\r\n"


def test_empty_records_still_include_header():
    assert export_records_csv([], ["id", "name"]) == "id,name\r\n"


def test_mismatched_record_schema():
    with pytest.raises(ValueError):
        export_records_csv([{"id": 1}], ["id", "name"])
