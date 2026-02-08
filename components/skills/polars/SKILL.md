---
name: polars
description: Guide for writing optimized Polars code with correct syntax. This skill should be used when writing, reviewing, or refactoring Python code that uses the Polars DataFrame library.
---

# Polars

This skill provides guidance for writing correct, idiomatic, and performant Python code using the Polars DataFrame library.

## Core Principles

1. **Default to lazy evaluation** — Use `scan_*` functions and `.collect()` instead of `read_*` to enable query optimization (predicate pushdown, projection pushdown, parallel execution).
2. **Use expressions, not Python functions** — Polars expressions (`pl.col()`, `.str`, `.dt`, `.list`) run natively in Rust. Avoid `map_elements()` / `apply()` with Python lambdas — they force row-by-row Python execution and destroy performance.
3. **Batch operations in single contexts** — Combine multiple column operations in one `with_columns()` or `select()` call. Polars parallelizes independent expressions within a single context but must execute separate contexts sequentially.
4. **No index** — Polars DataFrames have no index. Do not attempt to set, reset, or rely on an index. Use `with_row_index()` to add a row number column when needed.
5. **Strict types** — Every column has a fixed dtype. Cast explicitly with `.cast()`. Mixed-type columns are not supported.

## Quick Reference

| Operation | Pattern |
|---|---|
| Select columns | `df.select("a", "b")` or `df.select(pl.col("a", "b"))` |
| Filter rows | `df.filter(pl.col("x") > 5)` |
| Add/modify columns | `df.with_columns((pl.col("a") + 1).alias("b"))` |
| Rename columns | `df.rename({"old": "new"})` |
| Sort | `df.sort("col")` or `df.sort("col", descending=True)` |
| Group + aggregate | `df.group_by("g").agg(pl.col("v").sum())` |
| Window function | `pl.col("v").sum().over("g")` |
| Conditional column | `pl.when(cond).then(a).otherwise(b)` |
| Join | `df1.join(df2, on="key", how="left")` |
| Concat | `pl.concat([df1, df2])` |
| Unique rows | `df.unique(subset=["col"])` |
| Value counts | `df["col"].value_counts()` |
| Null handling | `pl.col("x").fill_null(0)` / `df.drop_nulls()` |
| Type casting | `pl.col("x").cast(pl.Int64)` |
| String ops | `pl.col("s").str.to_lowercase()` |
| Date extraction | `pl.col("d").dt.year()` (note: parentheses required) |
| List ops | `pl.col("l").list.len()` / `df.explode("l")` |
| Row index | `df.with_row_index("idx")` |

## Lazy Evaluation

### When to Use Lazy

Default to lazy for any pipeline that reads from files, chains multiple transformations, or processes more than trivial amounts of data. Use eager (`pl.read_*`, direct DataFrame operations) only for quick interactive exploration or when the data is already in memory and the pipeline is a single step.

### The Scan-Transform-Collect Pattern

```python
result = (
    pl.scan_parquet("data/**/*.parquet")  # 1. Scan — no data read yet
    .filter(pl.col("date") >= "2024-01-01")  # 2. Transform — builds query plan
    .group_by("category")
    .agg(pl.col("revenue").sum())
    .sort("revenue", descending=True)
    .collect()  # 3. Collect — optimizes and executes
)
```

### Query Optimizations

The lazy engine automatically applies:
- **Predicate pushdown** — filters move to the scan level so unneeded rows are never read
- **Projection pushdown** — only referenced columns are loaded from disk
- **Expression simplification** — redundant operations are eliminated
- **Common subexpression elimination** — shared computations are reused

To inspect the plan: `lf.explain()` (optimized) or `lf.explain(optimized=False)` (raw).

For large datasets that exceed memory, use `collect(streaming=True)` or `sink_parquet()` / `sink_csv()` to write results without full materialization.

## Common Tasks

### Aggregation and Grouping

Use `group_by().agg()` with expression-based aggregations. Multiple aggregations go in a single `.agg()` call. To preserve input row order, pass `maintain_order=True` to `group_by()`.

To aggregate without grouping, use `df.select()` with aggregation expressions directly.

For ranked or cumulative operations within groups without collapsing rows, use `.over()` window expressions inside `with_columns()`.

### Joins

Use `df1.join(df2, on=..., how=...)`. For different column names, use `left_on` / `right_on`. For time-based nearest matching, use `join_asof()`. Use `how="semi"` or `how="anti"` for existence checks instead of joining and filtering.

### Reshaping

- **Wide to long**: `df.unpivot(on=[value_cols], index=[id_cols])`
- **Long to wide**: `df.pivot(on="category_col", values="value_col")`
- **Explode lists to rows**: `df.explode("list_col")`

### String and Temporal Operations

All string methods are on `.str` namespace, all datetime methods on `.dt` namespace. These are expression-native — do not extract to Python strings/dates to process them.

For parsing strings to dates: `pl.col("s").str.to_date("%Y-%m-%d")` or `pl.col("s").str.to_datetime(...)`.

For date arithmetic: `pl.col("d") + pl.duration(days=7)`.

## Anti-Patterns and Corrections

1. **Instead of** `df.apply(lambda row: ..., axis=1)`, **use** expression chains (`pl.col()`, `when/then/otherwise`, `.str`, `.dt`). Native expressions are orders of magnitude faster.

2. **Instead of** `df.with_columns(pl.col("x").map_elements(lambda v: v * 2))`, **use** `df.with_columns(pl.col("x") * 2)`. Any arithmetic, comparison, or built-in operation has a native expression equivalent.

3. **Instead of** chaining multiple separate `with_columns()` calls for independent columns, **combine** them into one `with_columns()`. One context = parallel execution.

4. **Instead of** `pl.read_csv("large.csv")` followed by filtering, **use** `pl.scan_csv("large.csv").filter(...).collect()`. Lazy mode pushes predicates and projections down to the reader.

5. **Instead of** `.to_pandas()` to use a pandas operation then converting back, **find** the Polars-native equivalent. Conversion is expensive and loses Polars optimizations. Consult `references/polars-api-patterns.md` for the Polars equivalent.

6. **Instead of** iterating rows with `for row in df.iter_rows()` to compute values, **use** vectorized expressions. Row iteration bypasses the expression engine entirely.

7. **Instead of** `df["col"]` for column selection in pipelines, **use** `pl.col("col")` inside `select()` / `with_columns()` / `filter()`. Bracket indexing returns a Series and breaks expression chains.

8. **Instead of** treating NaN and null as interchangeable, **handle them separately**. Use `fill_null()` for null values and `fill_nan()` for NaN. To unify, convert NaN to null first with `fill_nan(None)`.

9. **Instead of** `df.groupby(...)`, **use** `df.group_by(...)`. Polars uses `group_by` (with underscore), not the pandas `groupby`.

10. **Instead of** building multiple lazy queries and collecting each separately, **combine** them into a single query plan where possible. Each `.collect()` is an optimization barrier.

## References

For detailed API syntax with code examples for each operation category, consult `references/polars-api-patterns.md`. Key sections to search for:
- `## Expression Fundamentals` — `pl.col()`, selectors, aliasing
- `## Lazy Evaluation Patterns` — scan functions, explain, sink
- `## Aggregation Patterns` — group_by, window functions with `.over()`
- `## Join Patterns` — all join types, asof joins
- `## Conditional Logic` — when/then/otherwise, replace
- `## String Operations` — `.str` namespace methods
- `## Temporal Operations` — `.dt` namespace methods
- `## List Operations` — `.list` namespace methods
- `## Struct Operations` — `.struct` namespace, unnest
- `## Type Casting` — cast, categoricals, shrink_dtype
- `## Null and NaN Handling` — fill_null, fill_nan, coalesce
- `## Performance Patterns` — streaming, memory, parallelism
- `## pandas-to-Polars Migration` — side-by-side operation table
