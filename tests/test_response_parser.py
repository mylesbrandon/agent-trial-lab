import pytest

from agents.response_parser import extract_python_source


def test_plain_python_response_parses():
    response = "def rolling_zscore(values, window):\n    return []"

    extracted = extract_python_source(response)

    assert extracted == response + "\n"


def test_single_fenced_python_response_parses():
    response = (
        "```python\n"
        "def rolling_zscore(values, window):\n"
        "    return []\n"
        "```"
    )

    extracted = extract_python_source(response)

    assert extracted == (
        "def rolling_zscore(values, window):\n"
        "    return []\n"
    )


def test_multiple_code_blocks_are_rejected():
    response = (
        "```python\nvalue = 1\n```\n"
        "```python\nvalue = 2\n```"
    )

    with pytest.raises(ValueError, match="multiple code blocks"):
        extract_python_source(response)


def test_syntax_error_is_rejected_without_repair():
    response = "def broken(:\n    pass"

    with pytest.raises(ValueError, match="not valid Python"):
        extract_python_source(response)


def test_empty_response_is_rejected():
    with pytest.raises(ValueError, match="did not contain code"):
        extract_python_source("  \n")
