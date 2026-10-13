# Task 027: Stable CSV Deduplication by Composite Key

Implement `deduplicate_csv(text, key_columns, keep="last")`.
`keep` must be `"first"` or `"last"`. `key_columns` must be a nonempty
list or tuple of distinct nonempty strings. Invalid arguments raise
`ValueError` before parsing, including for empty text.

Empty or whitespace-only text returns `[]`. Otherwise the first CSV
record is a header: strip each name, reject empty or duplicate names,
and require every key column to occur in the header. Names and values
are case-sensitive. Use strict standard CSV parsing, honoring quoted
commas, doubled quotes, and embedded newlines. Skip empty records and
records with a single whitespace-only field. Reject incorrect data
widths and CSV parsing errors with `ValueError`. Strip every field;
empty field strings are valid, including key fields.

A key is the tuple of values from all key columns, after stripping.
Return a list of dictionaries, keeping either the first or last entire
record for each key. Output key groups in order of their FIRST occurrence,
including when `keep="last"`; replacing a record must not move its group.
Preserve all header columns in their header order. A header without data
returns `[]`. Do not modify `key_columns`.
