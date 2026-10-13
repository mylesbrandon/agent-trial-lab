import pytest
from starter import parse_utf8_csv_chunks


def test_every_byte_boundary_in_unicode_and_bom():
    data = '\ufeffid,name\n1,café 🐍\n'.encode('utf-8')
    expected = [{"id": "1", "name": "café 🐍"}]
    for split in range(len(data) + 1):
        assert parse_utf8_csv_chunks([data[:split], data[split:]]) == expected


def test_bytewise_quoted_multiline_and_crlf():
    data = b'id,note\r\n1,"a,b\r\nsay ""hi"""\r\n'
    assert parse_utf8_csv_chunks(bytes([b]) for b in data) == [{"id": "1", "note": 'a,b\r\nsay "hi"'}]


def test_single_pass_iterable_and_whitespace_preservation():
    class Once:
        def __init__(self):
            self.used = False

        def __iter__(self):
            assert not self.used
            self.used = True
            return iter([b" id ,note\n a , \n"])
    assert parse_utf8_csv_chunks(Once()) == [{" id ": " a ", "note": " "}]


def test_invalid_and_truncated_utf8():
    for chunks in ([b'id\n', b'\xff'], [b'id\n1\n\xe2', b'\x82']):
        with pytest.raises(ValueError):
            parse_utf8_csv_chunks(chunks)


def test_empty_records_and_header_only():
    assert parse_utf8_csv_chunks([b'id\n\n1\n\n']) == [{"id": "1"}]
    assert parse_utf8_csv_chunks([b'id\n']) == []


def test_invalid_header_and_width():
    for data in (b'id,id\n1,2\n', b'id,\n1,2\n', b'\nid\n', b'id,x\n1\n', b'id\n1,2\n'):
        with pytest.raises(ValueError):
            parse_utf8_csv_chunks([data])


def test_unterminated_quote_at_end_of_stream():
    with pytest.raises(ValueError):
        parse_utf8_csv_chunks([b'id,x\n1,"', b'not finished'])


def test_interior_bom_is_preserved_as_data():
    data = '\ufeffid,name\n1,a\ufeffb\n'.encode('utf-8')
    assert parse_utf8_csv_chunks(bytes([byte]) for byte in data) == [
        {"id": "1", "name": "a\ufeffb"}]
