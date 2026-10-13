import copy
import csv
import io
import pytest
from starter import export_records_csv


def test_quoted_commas_quotes_cr_and_lf_roundtrip():
    values = ['a,b', 'say "hi"', 'line\nnext', 'x\ry']
    output = export_records_csv([{"v": value} for value in values], ["v"])
    assert list(csv.reader(io.StringIO(output, newline=""))) == [["v"]] + [[value] for value in values]
    assert '"a,b"\r\n' in output
    assert '"say ""hi"""\r\n' in output
    assert '"x\ry"\r\n' in output


def test_formula_strings_after_whitespace_are_prefixed():
    values = ["=1+1", " +2", "\n-2", "\t@x", "\rhello", "\tplain"]
    output = export_records_csv([{"v": value} for value in values], ["v"])
    assert list(csv.reader(io.StringIO(output, newline="")))[1:] == [["'" + value] for value in values]


def test_negative_numbers_are_distinct_from_numeric_strings():
    output = export_records_csv([{"n": -2, "s": "-2", "f": -1.5}], ["n", "s", "f"])
    assert output == "n,s,f\r\n-2,'-2,-1.5\r\n"


def test_none_empty_apostrophe_and_plain_strings():
    values = [None, "", "'=1", "hello", "  "]
    output = export_records_csv([{"v": value} for value in values], ["v"])
    assert list(csv.reader(io.StringIO(output, newline="")))[1:] == [[""], [""], ["'=1"], ["hello"], ["  "]]


def test_invalid_values_rejected():
    for value in (True, False, float("nan"), float("inf"), float("-inf"), [], {}):
        with pytest.raises(ValueError):
            export_records_csv([{"v": value}], ["v"])


def test_invalid_columns_and_extra_keys():
    for columns in ([], ["x", "x"], [""], [1], "x"):
        with pytest.raises(ValueError):
            export_records_csv([], columns)
    with pytest.raises(ValueError):
        export_records_csv([{"x": 1, "y": 2}], ["x"])


def test_headers_are_literal_and_inputs_unchanged():
    records = [{"=header": "=value", "b": None}]
    saved = copy.deepcopy(records)
    columns = ["=header", "b"]
    assert export_records_csv(iter(records), columns) == "=header,b\r\n'=value,\r\n"
    assert records == saved
    assert columns == ["=header", "b"]
