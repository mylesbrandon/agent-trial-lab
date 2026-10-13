# Task 028: Parse CSV Across Arbitrary UTF-8 Byte Chunks

Implement `parse_utf8_csv_chunks(chunks)`. `chunks` is a single-pass
iterable of `bytes`; raise `ValueError` for any non-bytes item. Consume
the iterable once. Empty chunks are permitted. Treat their concatenation
as one UTF-8 CSV document. Strip one leading BOM; interior U+FEFF is
preserved as ordinary data. A byte
chunk may split a multibyte character, BOM, CRLF pair, quoted field,
doubled quote, or embedded newline. Invalid or incomplete UTF-8 raises
`ValueError`, including after otherwise complete rows. Buffering the
complete document is allowed; no streaming memory bound is required.

Empty decoded text returns `[]`. Otherwise the first CSV record is the
header, whose names must be distinct nonempty strings. Preserve names
and values exactly: do not trim whitespace or change case. Use strict
standard CSV parsing, including quoted commas, doubled quotes, and
embedded newlines. Skip empty records only (`[]` from the CSV reader);
a whitespace field is real data. Other records must match header width.
Invalid headers, row widths, or malformed CSV raise `ValueError`.
Return a list of dictionaries in row order and header key order. A
header without data returns `[]`.
