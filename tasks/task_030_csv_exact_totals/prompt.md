# Task 030: Aggregate Exact Decimal Amounts from CSV

Implement `aggregate_payments_csv(text)`. Empty or whitespace-only input
returns `[]`. Otherwise require header `group,amount` after stripping
header whitespace, in that exact order. Use strict standard CSV quoting
(commas, doubled quotes, embedded newlines). Skip empty records and
single-field whitespace-only records. Other records must have two fields.
Strip field whitespace. Group names are case-sensitive nonempty strings.
Invalid headers, widths, blank groups, or CSV errors raise `ValueError`.

A nonempty amount must match `[+-]?[0-9]+(?:\.[0-9]{1,2})?`: an optional
sign, at least one ASCII integer digit, and optionally one or two decimal
digits. Exponents, separators, NaN, infinity, and more than two fractional
digits are invalid and raise `ValueError`. Integers have no size limit
beyond Python's ordinary integer support. Amounts must be summed exactly,
without binary floating-point rounding. Missing amounts (empty strings)
contribute neither value nor count, but still establish a group.

Return dictionaries with `group`, `total`, and `count`, one per group in
order of FIRST appearance. `count` is the number of nonmissing amounts.
`total` is a signed decimal string with exactly two fractional digits,
no plus sign or unnecessary leading zeroes, and zero written `"0.00"`
(never negative zero). An all-missing group has total `"0.00"`, count 0.
A header without data returns `[]`.
