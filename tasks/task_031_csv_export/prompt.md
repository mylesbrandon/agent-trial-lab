# Task 031: Deterministic CSV Serialization with Formula-String Escaping

Implement `export_records_csv(records, columns)` using the standard library.
`columns` is a nonempty list or tuple of distinct nonempty strings.
`records` is an iterable of dictionaries, each containing exactly those
keys. Validate schema arguments and every record, raising `ValueError`
for invalid columns, missing or extra keys, or unsupported values. Do not
mutate either input. Preserve row order and the supplied column order.

Values may be `None`, strings, built-in integers (not bools), or finite
built-in floats. None becomes an empty field. Numbers use Python `str()`
formatting, so numeric negative values remain numeric text. Booleans,
NaN, infinity, lists, and other value types are invalid.

For string VALUES only, prepend one apostrophe to the complete original
value if either (a) after removing leading spaces, tabs, carriage returns,
and newlines it starts with `=`, `+`, `-`, or `@`, or (b) its very first
character is a tab or carriage return. Preserve original whitespace and
content after that prefix. Already-apostrophe-prefixed strings remain
unchanged. Header names are serialized literally, without this escaping.
This is a precise transformation contract, not a guarantee about every
spreadsheet application's behavior.

Return one CSV string containing a header, including for no data records.
Use a comma delimiter, double-quote quote character, doubled embedded
quotes, and minimal quoting. Fields containing comma, quote, CR or LF
must be quoted. Use CRLF (`\r\n`) record terminators, including a final
terminator. Do not add a BOM. Embedded newlines within values remain intact.
