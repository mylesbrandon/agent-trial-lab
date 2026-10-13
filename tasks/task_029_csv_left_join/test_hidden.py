import pytest
from starter import left_join_csv


def test_repeated_left_ids_preserve_order():
    assert left_join_csv("id,value\nb,1\na,2\nb,3\n", "id,label\nb,B\na,A\nc,C\n") == [
        {"id": "b", "value": "1", "label": "B"}, {"id": "a", "value": "2", "label": "A"},
        {"id": "b", "value": "3", "label": "B"}]


def test_duplicate_right_ids_rejected_after_stripping():
    with pytest.raises(ValueError):
        left_join_csv("id,value\na,1\n", "id,label\na,X\n a ,X\n")


def test_right_validated_when_left_empty_or_key_unmatched():
    for left in ("", "id,value\nz,1\n"):
        with pytest.raises(ValueError):
            left_join_csv(left, "id,label\na,X\na,Y\n")


def test_matched_empty_label_is_not_none():
    assert left_join_csv("id,value\na,\nb,2\n", "id,label\na,\n") == [
        {"id": "a", "value": "", "label": ""}, {"id": "b", "value": "2", "label": None}]


def test_quotes_newlines_and_case_sensitive_ids():
    left = 'id,value\na,"x,y"\nA,"line\nnext"\n'
    assert left_join_csv(left, 'id,label\na,"say ""yes"""\n') == [
        {"id": "a", "value": "x,y", "label": 'say "yes"'},
        {"id": "A", "value": "line\nnext", "label": None}]


def test_blank_rows_and_normalization():
    assert left_join_csv(" id , value \n\n a , 1 \n", "id,label\n a , A \n") == [
        {"id": "a", "value": "1", "label": "A"}]


def test_bad_width_blank_ids_and_quotes():
    for left in ("id,value\na\n", "id,value\na,1,x\n", "id,value\n ,1\n", 'id,value\na,"oops'):
        with pytest.raises(ValueError):
            left_join_csv(left, "")
    with pytest.raises(ValueError):
        left_join_csv("", "id,label\n ,A\n")
