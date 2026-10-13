import pytest
from starter import parse_csv_schema


def test_duplicate_header_after_normalization():
    with pytest.raises(ValueError):
        parse_csv_schema("id,ID\n1,2\n", ["id"])


def test_bom_and_header_only():
    assert parse_csv_schema("\ufeffid,name\n", ["id", "name"]) == []
    assert parse_csv_schema("\ufeffid\nx\n", ["id"]) == [{"id": "x"}]


def test_quoted_commas_quotes_and_newlines():
    text = 'id,note\n1,"a,b"\n2,"say ""hi""\nnext"\n'
    assert parse_csv_schema(text, ["id", "note"]) == [
        {"id": "1", "note": "a,b"}, {"id": "2", "note": 'say "hi"\nnext'}]


def test_blank_records_and_empty_fields():
    assert parse_csv_schema("id,note\n\n   \n1,\n,ok\n", ["id", "note"]) == [
        {"id": "1", "note": ""}, {"id": "", "note": "ok"}]


def test_bad_width_extra_header_and_malformed_quotes():
    for text in ('id,name\n1\n', 'id,name\n1,2,3\n', 'id,name,x\n1,a,b\n', 'id,name\n1,"oops'):
        with pytest.raises(ValueError):
            parse_csv_schema(text, ["id", "name"])


def test_schema_validation_precedes_empty_input():
    for columns in ([], ["id", "id"], ["ID"], [""], [2], "id"):
        with pytest.raises(ValueError):
            parse_csv_schema("", columns)


def test_output_key_order_and_schema_unchanged():
    columns = ["b", "a"]
    result = parse_csv_schema("a,b\nx,y\n", columns)
    assert list(result[0]) == ["b", "a"]
    assert result == [{"b": "y", "a": "x"}]
    assert columns == ["b", "a"]
