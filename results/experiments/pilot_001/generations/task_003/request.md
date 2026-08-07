You are solving a Python code-repair benchmark task.

Follow the written specification exactly.

Return only the complete contents of starter.py after your repair.
Do not include Markdown fences, explanations, tests, or commentary.

TASK SPECIFICATION
------------------
# Task 003: Repair Lookahead-Safe Strategy Returns

Repair the `strategy_returns(prices, signals, transaction_cost=0.0)`
function in `starter.py`.

The function calculates simple strategy returns from an asset-price
series and a desired-position series. The implementation must not use
future information.

## Inputs

* `prices` is a Python list or tuple of asset prices.
* `signals` is a Python list or tuple containing the desired position
  at each corresponding timestamp.
* `prices` and `signals` must have equal length. Raise `ValueError`
  when their lengths differ.
* Every price must be a positive number. Raise `ValueError` when a
  price is zero, negative, or nonnumeric.
* Every signal must be numeric. Raise `ValueError` when a signal is
  nonnumeric.
* Positions may be negative, zero, or positive.
* `transaction_cost` is a proportional cost per unit of position
  turnover. Raise `ValueError` when it is negative.

## Return Alignment

Return a list with the same length as `prices`. Empty inputs return an
empty list.

The first output is always:

```text
returns[0] = 0.0
```

For every later index `t`, first calculate the simple asset return:

```text
asset_return[t] = prices[t] / prices[t - 1] - 1
```

The price movement from index `t - 1` to index `t` occurs after the
signal at `t - 1` is known. Therefore, that interval must use the
previous timestamp's signal:

```text
position[t] = signals[t - 1]
gross_strategy_return[t] = position[t] * asset_return[t]
```

A signal calculated at index `t` must never affect the return ending
at index `t`. Using `signals[t]` for that already-realized price
movement introduces lookahead bias.

## Transaction-Cost Convention

The initial establishment of `signals[0]` is not charged. As a result,
turnover and cost are both zero at output index `1`.

Beginning at output index `2`, charge proportional cost for the
position change that occurred at the start of the return interval:

```text
turnover[t] = abs(signals[t - 1] - signals[t - 2])
cost[t] = transaction_cost * turnover[t]
```

Thus, for `t >= 1`:

```text
returns[t] = (
    signals[t - 1] * asset_return[t]
    - cost[t]
)
```

where `cost[1]` is `0.0`.

Transaction cost depends on the size of the position change, not just
on whether a change occurred. Costs are still charged when prices are
flat.


STARTER CODE
------------
def strategy_returns(prices, signals, transaction_cost=0.0):
    """
    Calculate strategy returns from prices and desired positions.

    This implementation contains alignment and transaction-cost bugs
    that must be repaired.
    """
    if len(prices) != len(signals):
        raise ValueError("prices and signals must have equal length")

    if transaction_cost < 0:
        raise ValueError("transaction_cost cannot be negative")

    if not prices:
        return []

    results = [0.0]

    for i in range(1, len(prices)):
        asset_return = prices[i] / prices[i - 1] - 1

        # Bug: the current signal was not known before this return.
        strategy_return = signals[i] * asset_return

        # Bug: this charges at the wrong time and ignores turnover size.
        if signals[i] != signals[i - 1]:
            strategy_return -= transaction_cost

        results.append(strategy_return)

    return results


PUBLIC TESTS
------------
import pytest

from starter import strategy_returns


def test_constant_long_position():
    result = strategy_returns(
        [100, 110, 121],
        [1, 1, 1],
    )

    assert result == pytest.approx([0.0, 0.10, 0.10])


def test_constant_short_position():
    result = strategy_returns([100, 90], [-1, -1])

    assert result == pytest.approx([0.0, 0.10])


def test_unequal_lengths_raise_value_error():
    with pytest.raises(ValueError):
        strategy_returns([100, 110], [1])


def test_negative_transaction_cost_raises_value_error():
    with pytest.raises(ValueError):
        strategy_returns([100], [1], transaction_cost=-0.01)


def test_empty_input_returns_empty_list():
    assert strategy_returns([], []) == []


def test_tuple_inputs_return_matching_length():
    result = strategy_returns((100, 105), (2, 2))

    assert isinstance(result, list)
    assert result == pytest.approx([0.0, 0.10])

