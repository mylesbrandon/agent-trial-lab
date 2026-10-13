# Task catalog

Each row is a distinct task. Test counts come from the checked-in metadata and are verified against executed reference suites by `python runner/check_quality.py`.

| Task | Contract | Area | Public | Hidden |
|---|---|---|---:|---:|
| task_001 | [Rolling Z-Score](../tasks/task_001_rolling_zscore/prompt.md) | Numerical robustness | 3 | 8 |
| task_002 | [Repair a Shortest-Path Function](../tasks/task_002_shortest_path/prompt.md) | Graph algorithms | 5 | 8 |
| task_003 | [Repair Lookahead-Safe Strategy Returns](../tasks/task_003_signal_alignment/prompt.md) | Time-series alignment | 6 | 10 |
| task_004 | [Repair Market CSV Parsing](../tasks/task_004_market_csv/prompt.md) | CSV parsing | 4 | 10 |
| task_005 | [Stable Softmax with Infinite Scores](../tasks/task_005_stable_softmax/prompt.md) | Numerical robustness | 3 | 10 |
| task_006 | [Scale-Safe Weighted Mean](../tasks/task_006_weighted_mean/prompt.md) | Numerical robustness | 3 | 11 |
| task_007 | [Interpolated Quantiles](../tasks/task_007_linear_quantile/prompt.md) | Numerical robustness | 3 | 9 |
| task_008 | [Range Normalization Without Overflow](../tasks/task_008_minmax_scale/prompt.md) | Numerical robustness | 3 | 9 |
| task_009 | [Overflow-Safe Euclidean Norm](../tasks/task_009_euclidean_norm/prompt.md) | Numerical robustness | 3 | 8 |
| task_010 | [Merge Streaming Variance Summaries](../tasks/task_010_merge_moments/prompt.md) | Numerical robustness | 3 | 9 |
| task_011 | [Precise Histogram Edge Assignment](../tasks/task_011_histogram_edges/prompt.md) | Numerical robustness | 3 | 8 |
| task_012 | [Lexicographic Topological Ordering](../tasks/task_012_topological_order/prompt.md) | Graph algorithms | 3 | 7 |
| task_013 | [Strongly Connected Components](../tasks/task_013_strong_components/prompt.md) | Graph algorithms | 3 | 7 |
| task_014 | [Deterministic Minimum Spanning Forest](../tasks/task_014_spanning_forest/prompt.md) | Graph algorithms | 3 | 8 |
| task_015 | [Canonical Bipartite Coloring](../tasks/task_015_bipartite_coloring/prompt.md) | Graph algorithms | 3 | 8 |
| task_016 | [Bridge Edges in an Undirected Multigraph](../tasks/task_016_multigraph_bridges/prompt.md) | Graph algorithms | 3 | 8 |
| task_017 | [Multi-Source Directed Distance Layers](../tasks/task_017_distance_layers/prompt.md) | Graph algorithms | 3 | 8 |
| task_018 | [Earliest Completion Times in a Dependency DAG](../tasks/task_018_dag_finish_times/prompt.md) | Graph algorithms | 3 | 9 |
| task_019 | [Backward As-of Alignment](../tasks/task_019_backward_asof/prompt.md) | Time-series alignment | 4 | 8 |
| task_020 | [Duration-weighted Causal Means](../tasks/task_020_time_weighted_mean/prompt.md) | Time-series alignment | 4 | 9 |
| task_021 | [Fixed-bin OHLC Resampling](../tasks/task_021_fixed_bin_ohlc/prompt.md) | Time-series alignment | 4 | 8 |
| task_022 | [Lagged Rolling Means with Missing Observations](../tasks/task_022_lagged_rolling_mean/prompt.md) | Time-series alignment | 4 | 9 |
| task_023 | [Forward Fill with Observation Age Limits](../tasks/task_023_bounded_forward_fill/prompt.md) | Time-series alignment | 4 | 8 |
| task_024 | [Purged Temporal Train/Test Split](../tasks/task_024_purged_time_split/prompt.md) | Time-series alignment | 4 | 9 |
| task_025 | [Elapsed Drawdown Durations](../tasks/task_025_drawdown_durations/prompt.md) | Time-series alignment | 4 | 8 |
| task_026 | [Normalize and Validate a CSV Schema](../tasks/task_026_csv_schema/prompt.md) | CSV parsing | 3 | 7 |
| task_027 | [Stable CSV Deduplication by Composite Key](../tasks/task_027_csv_deduplication/prompt.md) | CSV parsing | 3 | 7 |
| task_028 | [Parse CSV Across Arbitrary UTF-8 Byte Chunks](../tasks/task_028_utf8_csv_chunks/prompt.md) | CSV parsing | 3 | 8 |
| task_029 | [Validated Many-to-One CSV Left Join](../tasks/task_029_csv_left_join/prompt.md) | CSV parsing | 3 | 7 |
| task_030 | [Aggregate Exact Decimal Amounts from CSV](../tasks/task_030_csv_exact_totals/prompt.md) | CSV parsing | 3 | 7 |
| task_031 | [Deterministic CSV Serialization with Formula-String Escaping](../tasks/task_031_csv_export/prompt.md) | CSV parsing | 3 | 7 |
| task_032 | [Pivot Long CSV Records into a Deterministic Wide Table](../tasks/task_032_csv_pivot/prompt.md) | CSV parsing | 3 | 7 |

**Total: 32 tasks, 109 public and 264 hidden tests (373 total).**

The original four-task pilot remains scoped to Tasks 001–004. The expanded corpus does not retroactively change that experiment.
