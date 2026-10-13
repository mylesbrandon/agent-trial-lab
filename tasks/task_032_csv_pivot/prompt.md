# Task 032: Pivot Long CSV Records into a Deterministic Wide Table

Implement `pivot_csv(text, fill="")`. `text` is CSV in long form with
exactly the header `row,column,value`, in that order after stripping
header whitespace. Empty or whitespace-only text and a header with no
data return `[["row"]]`. `fill` must be a string, or raise `ValueError`,
even for empty text.

Use strict standard CSV parsing, honoring quoted commas, doubled quotes,
and embedded newlines. Skip empty records and single-field whitespace-only
records. Reject malformed CSV, wrong headers, or data records whose width
is not three with `ValueError`. Strip surrounding whitespace from all
data fields. Row and column names must be nonempty and are case-sensitive.
The column name `row` is reserved and invalid; a ROW name of `row` is valid.

Return a rectangular list of lists of strings. The first row is `"row"`
followed by distinct column names in order of FIRST appearance in the
entire input. Later rows are distinct row names in order of FIRST
appearance, followed by their cell values in that same column order.
A cell absent from the input uses `fill` exactly, without stripping it.
A present empty value remains `""` and must not be replaced by `fill`.

A repeated `(row, column)` pair after stripping is invalid and must raise
`ValueError`, even when the two values are equal. Do not aggregate,
overwrite, sort, or silently drop duplicates. Late columns must appear
in every output row. Parse values as strings; no numeric conversion.
