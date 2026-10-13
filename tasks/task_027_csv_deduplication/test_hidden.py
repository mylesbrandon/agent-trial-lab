import pytest
from starter import deduplicate_csv


def test_last_replacement_keeps_first_group_order():
    assert deduplicate_csv("id,x\na,old\nb,mid\na,new\n", ["id"]) == [
        {"id": "a", "x": "new"}, {"id": "b", "x": "mid"}]


def test_composite_keys_do_not_collide():
    text = "a,b,x\nab,c,1\na,bc,2\nab,c,3\n"
    assert deduplicate_csv(text, ["a", "b"]) == [
        {"a": "ab", "b": "c", "x": "3"}, {"a": "a", "b": "bc", "x": "2"}]


def test_normalized_keys_empty_keys_and_case():
    text = "id,x\n a ,1\na,2\nA,3\n,4\n ,5\n"
    assert deduplicate_csv(text, ["id"]) == [
        {"id": "a", "x": "2"}, {"id": "A", "x": "3"}, {"id": "", "x": "5"}]


def test_quoted_values_and_blank_records():
    text = 'id,note\n\na,"x,y"\nb,"line\nnext"\na,"new ""quote"""\n'
    assert deduplicate_csv(text, ["id"]) == [
        {"id": "a", "note": 'new "quote"'}, {"id": "b", "note": "line\nnext"}]


def test_bad_headers_and_unknown_keys():
    for text in ("id,id\na,b\n", "id,\na,b\n", "x\na\n"):
        with pytest.raises(ValueError):
            deduplicate_csv(text, ["id"])


def test_bad_width_and_malformed_csv():
    for text in ('id,x\na\n', 'id,x\na,b,c\n', 'id,x\na,"oops'):
        with pytest.raises(ValueError):
            deduplicate_csv(text, ["id"])


def test_invalid_keys_and_no_parameter_mutation():
    for keys in ([], ["id", "id"], [""], [1], "id"):
        with pytest.raises(ValueError):
            deduplicate_csv("", keys)
    keys = ["x", "id"]
    assert deduplicate_csv("id,x\n", keys) == []
    assert keys == ["x", "id"]
