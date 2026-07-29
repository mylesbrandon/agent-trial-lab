import pytest

from starter import parse_market_csv


def test_quoted_comma_in_note():
    csv_text = '''timestamp,symbol,price,volume,note
2026-01-02,AAPL,195.25,100,"earnings, after close"
'''

    result = parse_market_csv(csv_text)

    assert result[0]["note"] == "earnings, after close"


def test_empty_price_becomes_none():
    csv_text = """timestamp,symbol,price,volume,note
2026-01-02,AAPL,,100,no price
"""

    result = parse_market_csv(csv_text)

    assert result[0]["price"] is None
    assert result[0]["volume"] == 100


def test_empty_volume_becomes_none():
    csv_text = """timestamp,symbol,price,volume,note
2026-01-02,AAPL,195.25,,
"""

    result = parse_market_csv(csv_text)

    assert result[0]["price"] == 195.25
    assert result[0]["volume"] is None
    assert result[0]["note"] == ""


def test_blank_lines_between_rows_are_skipped():
    csv_text = """timestamp,symbol,price,volume,note

2026-01-02,AAPL,195.25,100,first

2026-01-03,MSFT,420.50,50,second

"""

    result = parse_market_csv(csv_text)

    assert len(result) == 2
    assert [record["symbol"] for record in result] == ["AAPL", "MSFT"]


def test_whitespace_is_stripped_from_every_field():
    csv_text = """timestamp,symbol,price,volume,note
 2026-01-02 , msft , 420.50 , 7 , market update
"""

    assert parse_market_csv(csv_text) == [
        {
            "timestamp": "2026-01-02",
            "symbol": "MSFT",
            "price": 420.50,
            "volume": 7,
            "note": "market update",
        }
    ]


def test_lowercase_symbol_is_normalized():
    csv_text = """timestamp,symbol,price,volume,note
2026-01-02,tsla,450.0,25,test
"""

    assert parse_market_csv(csv_text)[0]["symbol"] == "TSLA"


def test_missing_or_incorrect_header_raises_value_error():
    invalid_inputs = [
        """timestamp,symbol,price,volume
2026-01-02,AAPL,195.25,100
""",
        """symbol,timestamp,price,volume,note
AAPL,2026-01-02,195.25,100,test
""",
    ]

    for csv_text in invalid_inputs:
        with pytest.raises(ValueError):
            parse_market_csv(csv_text)


def test_extra_column_raises_value_error():
    csv_text = """timestamp,symbol,price,volume,note
2026-01-02,AAPL,195.25,100,test,unexpected
"""

    with pytest.raises(ValueError):
        parse_market_csv(csv_text)


def test_invalid_integer_volume_raises_value_error():
    csv_text = """timestamp,symbol,price,volume,note
2026-01-02,AAPL,195.25,100.5,test
"""

    with pytest.raises(ValueError):
        parse_market_csv(csv_text)


def test_multiple_records_are_normalized():
    csv_text = """timestamp,symbol,price,volume,note
2026-01-02,aapl,195.25,100,first
2026-01-03, msft ,421.0,50,second
"""

    assert parse_market_csv(csv_text) == [
        {
            "timestamp": "2026-01-02",
            "symbol": "AAPL",
            "price": 195.25,
            "volume": 100,
            "note": "first",
        },
        {
            "timestamp": "2026-01-03",
            "symbol": "MSFT",
            "price": 421.0,
            "volume": 50,
            "note": "second",
        },
    ]
