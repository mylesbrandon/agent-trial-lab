# Controlled baseline failure analysis

These are deliberately flawed implementations used to check the test suites,
not model-generated attempts. Counts were reproduced on October 12, 2026 for
Tasks 001–004; see the [audit procedure](../reports/baseline-audit.md).

| Task | Implementation | Public passed | Hidden passed |
|---|---|---:|---:|
| 001 | reference_solution | 3/3 | 8/8 |
| 001 | no_zero_variance_handling | 3/3 | 7/8 |
| 001 | full_history_solution | 2/3 | 6/8 |
| 001 | no_nan_handling | 3/3 | 7/8 |
| 002 | reference_solution | 5/5 | 8/8 |
| 002 | no_relaxation_check | 5/5 | 4/8 |
| 002 | unreachable_returns_none | 5/5 | 5/8 |
| 003 | reference_solution | 6/6 | 10/10 |
| 003 | current_signal_lookahead | 6/6 | 5/10 |
| 003 | ignores_transaction_costs | 6/6 | 7/10 |
| 003 | flat_trade_cost | 6/6 | 8/10 |
| 004 | reference_solution | 4/4 | 10/10 |
| 004 | naive_split_solution | 4/4 | 9/10 |
| 004 | no_missing_value_handling | 4/4 | 8/10 |
| 004 | no_type_conversion | 2/4 | 5/10 |

## Task 001: Rolling Z-Score

The zero-variance defect fails hidden `test_constant_sequence_zero_variance`.
Singleton handling lets it pass the public first-position check.

The full-history defect fails public `test_basic_increasing_sequence` and
hidden `test_negative_values` and `test_uses_rolling_window_not_full_history`.
For `[1, 2, 3]` with a window of two, its final result is approximately 1.2247
instead of 1.0. The earlier claim that this baseline passed all public tests
was incorrect.

The NaN defect fails only hidden `test_nan_ignored_in_window`.
`test_nan_current_value_returns_nan` and `test_all_nan_input` pass through
ordinary NaN propagation. Their passing does not establish correct exclusion
of NaNs from otherwise usable windows. Two of the three defects demonstrate
a public-pass/hidden-fail result; the third is detected by both suites.

## Task 002: Shortest Path

Both defective baselines fail hidden `test_unreachable_target`,
`test_node_with_empty_adjacency_list`, and `test_graph_is_directed`.
`no_relaxation_check.py` also fails `test_duplicate_edges_choose_cheapest`.
It retains the starter's unreachable-result bug, so its failure count cannot
be attributed solely to relaxation. The documented Task 002 counts were
reproduced without changing its tests.

## Task 003: Lookahead-Safe Signal Alignment

The lookahead baseline fails
`test_signal_after_price_jump_cannot_earn_jump_return`,
`test_return_uses_previous_signal_when_signals_are_opposite`, and the three
cost tests below. The omitted-cost baseline fails
`test_transaction_cost_is_charged_when_new_position_is_used`,
`test_transaction_cost_scales_with_turnover`, and
`test_flat_prices_still_incur_position_change_costs`. The flat-cost baseline
fails the latter two. All three defects pass the public constant-position
examples. The documented Task 003 counts were reproduced.

## Task 004: Robust Market CSV Parsing

Naive splitting fails hidden `test_quoted_comma_in_note`. Missing-value
handling fails hidden `test_empty_price_becomes_none` and
`test_empty_volume_becomes_none`.

Missing type conversion fails public `test_basic_conversion` and
`test_invalid_price_raises_value_error`, plus hidden
`test_empty_price_becomes_none`, `test_empty_volume_becomes_none`,
`test_whitespace_is_stripped_from_every_field`,
`test_invalid_integer_volume_raises_value_error`, and
`test_multiple_records_are_normalized`. The whitespace test also asserts
numeric types, so its failure alone does not mean stripping is broken.

## Interpretation limits

For these original four tasks, all four references pass 54 distinct cases.
All 11 chosen defects fail hidden tests; nine pass public tests. These are
selected defects, not a random sample of possible implementation errors.
The 11/11 result must not be presented as a general bug-detection rate or as
model accuracy. Reference passes establish agreement on the evaluated cases,
not universal correctness.

The [frozen Pilot 001 analysis](experiments/pilot_001/analysis.md) concerns
separate manually captured submissions. Its four candidates failed during
collection before behavioral tests ran. This audit does not repair those
candidates or alter the pilot results. Newly added tasks require their own
validation and are outside this original-corpus audit.
