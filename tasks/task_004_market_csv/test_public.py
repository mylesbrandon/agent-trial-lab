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
