# Task 026: Normalize and Validate a CSV Schema

Implement `parse_csv_schema(text, columns)` using the standard library.
`text` is CSV text. `columns` is a list or tuple of distinct canonical
column names matching `[a-z][a-z0-9_]*`; it must not be empty. Invalid
schema arguments raise `ValueError`, even when the text is empty.

Empty or whitespace-only text returns `[]`. Remove one UTF-8 BOM character
(`\ufeff`) only if it is the very first character. The first CSV record
is the header. Strip header whitespace and apply `casefold()`. The
normalized header must contain exactly the requested columns, in any
order; duplicates, extra columns, missing columns, and empty names raise
`ValueError`. The supplied column order determines dictionary key order.

Parse using Python CSV quoting rules, including quoted commas, doubled
quotes, and embedded newlines. Use strict CSV parsing. Skip empty records
and records consisting of a single whitespace-only field. Every other
record must match the header width or raise `ValueError`. Strip each
field's surrounding whitespace, preserve empty fields as empty strings,
and return one dictionary of strings per data record in input order.
Convert CSV parse errors into `ValueError`. A header without data returns
`[]`. Do not modify `columns`.
