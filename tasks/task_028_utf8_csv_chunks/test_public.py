import pytest
from starter import parse_utf8_csv_chunks


def test_ascii_chunks():
    assert parse_utf8_csv_chunks([b"id,na", b"me\n1,Ada\n"]) == [{"id": "1", "name": "Ada"}]


def test_empty_chunks_and_document():
    assert parse_utf8_csv_chunks([b"", b""]) == []
    assert parse_utf8_csv_chunks([]) == []


def test_invalid_type():
    with pytest.raises(ValueError):
        parse_utf8_csv_chunks(["id\n1\n"])
