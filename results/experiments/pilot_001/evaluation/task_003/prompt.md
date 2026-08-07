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
