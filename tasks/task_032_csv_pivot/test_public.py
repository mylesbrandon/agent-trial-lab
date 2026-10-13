import pytest
from starter import pivot_csv


def test_basic_pivot():
    assert pivot_csv("row,column,value\na,x,1\na,y,2\nb,x,3\n") == [
        ["row", "x", "y"], ["a", "1", "2"], ["b", "3", ""]]


def test_empty_and_header_only():
    assert pivot_csv("") == [["row"]]
    assert pivot_csv("row,column,value\n") == [["row"]]


def test_wrong_header():
    with pytest.raises(ValueError):
        pivot_csv("row,value,column\na,1,x\n")
