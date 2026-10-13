# Task 018: Earliest Completion Times in a Dependency DAG

Repair `earliest_finish_times(graph, durations)` in `starter.py`.

`graph` maps string task names to lists of **dependent** tasks. An edge `u -> v`
means `v` cannot start before `u` finishes. `durations` maps each task to its own
processing duration. Assume unlimited workers, all roots may start at time zero,
and a task may start immediately when all its prerequisites finish.

Return a dictionary of earliest finish times for every task. A root finishes at
its duration; any other task finishes at its own duration plus the **maximum**
finish time among its direct prerequisites. Dictionary ordering is not significant.

* Disconnected components run independently. An empty graph with empty durations
  returns `{}`. Zero durations and finite positive fractional durations are valid.
* Treat duplicate neighbors as a single dependency.
* Raise `ValueError` for any cycle, including a self-loop or disconnected cycle,
  or any neighbor that is not a graph key.
* Duration keys must equal graph keys exactly. Raise `ValueError` for missing or
  extra duration keys, values outside the supported range `[0, 1e100]`,
  nonfinite values, or values other than `int` or `float`. Booleans are invalid durations. Other input shapes are guaranteed.
* Do not mutate the graph, its neighbor lists, or the durations dictionary.

Example: `{"a": ["c"], "b": ["c"], "c": []}` with durations
`{"a": 2, "b": 5, "c": 1}` returns `{"a": 2, "b": 5, "c": 6}`.
