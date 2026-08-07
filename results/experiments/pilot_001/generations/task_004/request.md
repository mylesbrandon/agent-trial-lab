You are solving a Python code-repair benchmark task.

Follow the written specification exactly.

Return only the complete contents of starter.py after your repair.
Do not include Markdown fences, explanations, tests, or commentary.

TASK SPECIFICATION
------------------
# Task 004: Repair Market CSV Parsing

Repair the `parse_market_csv(csv_text)` function in `starter.py`.

The function receives CSV text containing market data and returns a
list of normalized Python dictionaries. CSV quoting rules are part of
the input format, so fields may contain commas when they are quoted.

## Input

The first CSV record is the header. It must contain exactly these five
columns, in this fixed order:

```text
timestamp,symbol,price,volume,note
```

Missing columns, additional columns, renamed columns, and a different
column order are incorrect headers and must raise `ValueError`.

Each later nonblank record contains values for those same five
columns. A row with too few or too many fields, or otherwise malformed
CSV, must raise `ValueError`.

Empty or whitespace-only input returns `[]`. Completely blank rows
between data records must be skipped.

## Normalization

For every data row:

* Strip surrounding whitespace from every value.
* Convert `symbol` to uppercase.
* Convert a nonempty `price` to `float`.
* Convert a nonempty `volume` to `int`.
* Convert an empty `price` or `volume` to `None`.
* Preserve `timestamp` and `note` as strings after stripping.
* Preserve an empty note as `""`.
* Preserve commas inside quoted fields.

Raise `ValueError` when a nonempty price is not a valid `float` or a
nonempty volume is not a valid `int`.

## Output

Return one normalized dictionary per nonblank data row:

```python
[
    {
        "timestamp": "2026-01-02",
        "symbol": "AAPL",
        "price": 195.25,
        "volume": 100,
        "note": "earnings, after close",
    }
]
```

Use Python's standard CSV parsing tools rather than splitting lines on
commas. A quoted field such as `"earnings, after close"` is one field,
not two.


STARTER CODE
------------
def parse_market_csv(csv_text):
    """
    Parse market CSV text into records.

    This implementation contains parsing, validation, and
    normalization bugs that must be repaired.
    """
    if not csv_text.strip():
        return []

    lines = csv_text.strip().splitlines()
    headers = lines[0].split(",")

    records = []

    for line in lines[1:]:
        if not line.strip():
            continue

        values = line.split(",")
        record = dict(zip(headers, values))
        records.append(record)

    return records


PUBLIC TESTS
------------
import pytest

from starter import parse_market_csv


def test_basic_conversion():
    csv_text = """timestamp,symbol,price,volume,note
2026-01-02,AAPL,195.25,100,earnings
"""

    assert parse_market_csv(csv_text) == [
        {
            "timestamp": "2026-01-02",
            "symbol": "AAPL",
            "price": 195.25,
            "volume": 100,
            "note": "earnings",
        }
    ]


def test_symbol_is_stripped_and_normalized():
    csv_text = """timestamp,symbol,price,volume,note
2026-01-02, aapl ,195.25,100,test
"""

    result = parse_market_csv(csv_text)

    assert result[0]["symbol"] == "AAPL"


def test_empty_or_whitespace_only_input_returns_empty_list():
    assert parse_market_csv("") == []
    assert parse_market_csv("   \n") == []


def test_invalid_price_raises_value_error():
    csv_text = """timestamp,symbol,price,volume,note
2026-01-02,AAPL,not-a-price,100,test
"""

    with pytest.raises(ValueError):
        parse_market_csv(csv_text)

