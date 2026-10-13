import pytest
from starter import pivot_csv


def test_first_occurrence_order_and_late_columns():
    assert pivot_csv("row,column,value\nz,b,1\na,a,2\nz,c,3\n", "NA") == [
        ["row", "b", "a", "c"], ["z", "1", "NA", "3"], ["a", "NA", "2", "NA"]]


def test_duplicate_cell_rejected_even_equal_after_stripping():
    with pytest.raises(ValueError):
        pivot_csv("row,column,value\na,x,1\n a , x ,1\n")


def test_missing_fill_differs_from_present_empty_value():
    assert pivot_csv("row,column,value\na,x,\nb,y,2\n", " missing ") == [
        ["row", "x", "y"], ["a", "", " missing "], ["b", " missing ", "2"]]


def test_quoted_commas_quotes_and_newlines():
    text = 'row,column,value\n"r,1","x,y","say ""hi"""\n"r,1",z,"line\nnext"\n'
    assert pivot_csv(text) == [["row", "x,y", "z"], ["r,1", 'say "hi"', "line\nnext"]]


def test_blank_records_normalization_and_case_sensitive_names():
    assert pivot_csv(" row , column , value \n\n a , X , 1 \na,x,2\nA,X,3\nrow,x,4\n") == [
        ["row", "X", "x"], ["a", "1", "2"], ["A", "3", ""], ["row", "", "4"]]


def test_blank_or_reserved_names_and_invalid_fill():
    for text in ("row,column,value\n ,x,1\n", "row,column,value\na, ,1\n", "row,column,value\na,row,1\n"):
        with pytest.raises(ValueError):
            pivot_csv(text)
    with pytest.raises(ValueError):
        pivot_csv("", None)


def test_wrong_width_and_malformed_csv():
    for text in ('row,column,value\na,x\n', 'row,column,value\na,x,1,2\n', 'row,column,value\na,x,"oops'):
        with pytest.raises(ValueError):
            pivot_csv(text)
