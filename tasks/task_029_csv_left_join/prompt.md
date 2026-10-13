# Task 029: Validated Many-to-One CSV Left Join

Implement `left_join_csv(left_text, right_text)`. The left CSV must have
header `id,value`; the right must have header `id,label`, in that order.
Strip surrounding whitespace from headers and values; names and IDs are
case-sensitive. Empty or whitespace-only text represents an empty table.
A header with no data is also empty. Use strict CSV parsing with quoted
commas, doubled quotes, and embedded newlines. Skip empty records and
single-field whitespace-only records. Reject all other incorrect row
widths, incorrect headers, malformed CSV, and blank data IDs with
`ValueError`.

Right-side IDs must be unique after stripping; duplicates raise
`ValueError`, even if labels agree or the ID never appears on the left.
Validate both inputs before returning, even when the left is empty.
Left-side repeated IDs are allowed and must produce repeated output rows.

Return one dictionary per left row, in left input order, with `id`,
`value`, and `label` keys. Matching labels are strings; a missing match
has label `None`, which differs from a matched empty label `""`.
Left rows must never be dropped or multiplied. A right-only ID produces
no output. All values remain strings except the missing label sentinel.
