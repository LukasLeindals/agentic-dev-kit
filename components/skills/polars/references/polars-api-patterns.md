# Polars API Patterns Reference

Comprehensive lookup reference for Polars operations. Each section includes correct syntax with code examples.

## Expression Fundamentals

### Column Selection

```python
# Single column
df.select(pl.col("name"))

# Multiple columns
df.select(pl.col("name", "age"))
df.select("name", "age")  # shorthand in select/with_columns

# All columns
df.select(pl.all())

# All except specific columns
df.select(pl.all().exclude("id", "timestamp"))

# By dtype
df.select(pl.col(pl.Utf8))        # all string columns
df.select(pl.col(pl.NUMERIC_DTYPES))  # all numeric columns

# By regex
df.select(pl.col("^feature_.*$"))
```

### Literals and Aliasing

```python
# Literal values
pl.lit(42)
pl.lit("constant")
pl.lit(None)

# Aliasing — rename expression output
pl.col("price").mean().alias("avg_price")

# Multiple aliases via name mapping
df.select(pl.col("name", "age").name.prefix("raw_"))
df.select(pl.col("name", "age").name.suffix("_v2"))
df.select(pl.all().name.map(str.upper))
```

### Column Selectors (`polars.selectors`)

```python
import polars.selectors as cs

# By dtype
df.select(cs.numeric())
df.select(cs.string())
df.select(cs.temporal())
df.select(cs.boolean())

# Combine selectors
df.select(cs.numeric() & ~cs.by_name("id"))
df.select(cs.string() | cs.temporal())

# By name pattern
df.select(cs.starts_with("feature_"))
df.select(cs.ends_with("_id"))
df.select(cs.contains("price"))
df.select(cs.matches("^col_\\d+$"))

# Set operations
df.select(cs.numeric() - cs.by_name("id"))  # difference
```

## Lazy Evaluation Patterns

### Creating Lazy Frames

```python
# From eager DataFrame
lf = df.lazy()

# Scan from file (preferred — enables predicate/projection pushdown)
lf = pl.scan_csv("data.csv")
lf = pl.scan_parquet("data.parquet")
lf = pl.scan_ndjson("data.ndjson")
lf = pl.scan_ipc("data.arrow")

# Scan with row count
lf = pl.scan_parquet("data.parquet").with_row_index("row_nr")

# Glob patterns for multiple files
lf = pl.scan_parquet("data/**/*.parquet")
```

### Query Plan Inspection

```python
# Print optimized query plan (text)
lf.explain()

# Print unoptimized plan
lf.explain(optimized=False)

# Visual graph (requires graphviz)
lf.show_graph()
lf.show_graph(optimized=False)
```

### Collecting Strategies

```python
# Standard collect — materializes entire result
result = lf.collect()

# Streaming collect — processes in batches, lower memory
result = lf.collect(streaming=True)

# Fetch N rows — useful for testing pipelines
sample = lf.fetch(n_rows=1000)

# Collect schema only (no data)
schema = lf.collect_schema()
```

### Sink Operations (Streaming Output)

```python
# Write results directly to file without full materialization
lf.sink_parquet("output.parquet")
lf.sink_csv("output.csv")
lf.sink_ndjson("output.ndjson")
lf.sink_ipc("output.arrow")
```

## Aggregation Patterns

### Basic Aggregation

```python
# Single aggregation
df.select(pl.col("price").mean())

# Multiple aggregations
df.select(
    pl.col("price").mean().alias("avg_price"),
    pl.col("price").std().alias("std_price"),
    pl.col("quantity").sum().alias("total_qty"),
    pl.len().alias("count"),
)
```

### Group By Aggregation

```python
# Basic group_by
df.group_by("category").agg(
    pl.col("price").mean().alias("avg_price"),
    pl.col("quantity").sum().alias("total_qty"),
    pl.len().alias("count"),
)

# Multiple grouping columns
df.group_by("category", "region").agg(
    pl.col("revenue").sum(),
)

# Maintain input order
df.group_by("category", maintain_order=True).agg(
    pl.col("price").mean(),
)

# First/last per group
df.group_by("category").agg(
    pl.col("price").first().alias("first_price"),
    pl.col("price").last().alias("last_price"),
)

# List of values per group
df.group_by("category").agg(
    pl.col("product").alias("products"),  # collects into list
)

# Aggregation with sorting inside groups
df.group_by("category").agg(
    pl.col("price").sort_by("date").last().alias("latest_price"),
)
```

### Window Functions with `.over()`

```python
# Running sum within groups (no collapse — keeps all rows)
df.with_columns(
    pl.col("price").sum().over("category").alias("category_total"),
)

# Rank within groups
df.with_columns(
    pl.col("score").rank().over("department").alias("dept_rank"),
)

# Multiple partition keys
df.with_columns(
    pl.col("value").mean().over("year", "region").alias("yr_region_avg"),
)

# Row number within groups
df.with_columns(
    pl.col("date").rank("ordinal").over("user_id").alias("visit_number"),
)

# Cumulative operations
df.with_columns(
    pl.col("revenue").cum_sum().over("store_id").alias("running_revenue"),
)

# Rolling window within groups
df.with_columns(
    pl.col("price").rolling_mean(window_size=7).over("product_id").alias("ma_7"),
)
```

## Join Patterns

### Join Types

```python
# Inner join
df1.join(df2, on="id", how="inner")

# Left join
df1.join(df2, on="id", how="left")

# Full outer join
df1.join(df2, on="id", how="full")

# Cross join
df1.join(df2, how="cross")

# Semi join (keep rows in left that have match in right)
df1.join(df2, on="id", how="semi")

# Anti join (keep rows in left that have NO match in right)
df1.join(df2, on="id", how="anti")
```

### Multiple Keys and Different Column Names

```python
# Multiple join keys
df1.join(df2, on=["id", "date"], how="inner")

# Different column names
df1.join(df2, left_on="user_id", right_on="id", how="left")

# Multiple different names
df1.join(
    df2,
    left_on=["user_id", "order_date"],
    right_on=["id", "date"],
    how="inner",
)

# Suffix for duplicate columns
df1.join(df2, on="id", how="left", suffix="_right")

# Coalesce join keys (avoid duplicate key columns in full join)
df1.join(df2, on="id", how="full", coalesce=True)
```

### Asof Joins

```python
# Join on nearest key (e.g., timestamp matching)
trades.join_asof(
    quotes,
    on="timestamp",
    by="ticker",          # exact match on this column
    strategy="backward",  # use most recent quote before/at trade time
)

# With tolerance
trades.join_asof(
    quotes,
    on="timestamp",
    strategy="backward",
    tolerance="5m",  # max 5 minutes apart
)
```

## Conditional Logic

### `when` / `then` / `otherwise`

```python
# Simple conditional
df.with_columns(
    pl.when(pl.col("score") >= 90)
    .then(pl.lit("A"))
    .when(pl.col("score") >= 80)
    .then(pl.lit("B"))
    .when(pl.col("score") >= 70)
    .then(pl.lit("C"))
    .otherwise(pl.lit("F"))
    .alias("grade"),
)

# Conditional with expressions
df.with_columns(
    pl.when(pl.col("type") == "premium")
    .then(pl.col("price") * 0.9)
    .otherwise(pl.col("price"))
    .alias("final_price"),
)

# Multiple conditions combined
df.with_columns(
    pl.when((pl.col("age") >= 18) & (pl.col("verified") == True))
    .then(pl.lit("eligible"))
    .otherwise(pl.lit("ineligible"))
    .alias("status"),
)
```

### Value Mapping with `.replace()`

```python
# Map specific values (dict-based)
df.with_columns(
    pl.col("status").replace({
        "A": "Active",
        "I": "Inactive",
        "P": "Pending",
    }).alias("status_label"),
)

# With default for unmapped values
df.with_columns(
    pl.col("code").replace(
        {"US": "United States", "UK": "United Kingdom"},
        default="Other",
    ).alias("country"),
)
```

## String Operations (`.str`)

```python
# Contains / starts_with / ends_with
pl.col("name").str.contains("pattern")          # regex by default
pl.col("name").str.contains("literal", literal=True)
pl.col("name").str.starts_with("prefix")
pl.col("name").str.ends_with("suffix")

# Extract with regex (capture group)
pl.col("email").str.extract(r"@(.+)\.", group_index=1)

# Replace
pl.col("text").str.replace("old", "new")         # first occurrence
pl.col("text").str.replace_all("old", "new")      # all occurrences

# Split
pl.col("tags").str.split(",")                     # returns list column
pl.col("path").str.split_exact("/", n=3)           # returns struct

# Case conversion
pl.col("name").str.to_uppercase()
pl.col("name").str.to_lowercase()
pl.col("name").str.to_titlecase()

# Strip whitespace
pl.col("text").str.strip_chars()
pl.col("text").str.strip_chars_start()
pl.col("text").str.strip_chars_end()

# Length
pl.col("name").str.len_chars()     # character count
pl.col("name").str.len_bytes()     # byte count

# Padding
pl.col("id").str.pad_start(5, "0")   # "42" -> "00042"

# Slice
pl.col("code").str.slice(0, 3)       # first 3 characters

# JSON parsing (from string column)
pl.col("json_str").str.json_decode(dtype=pl.Struct({"key": pl.Utf8}))
```

## Temporal Operations (`.dt`)

```python
# Component extraction
pl.col("date").dt.year()
pl.col("date").dt.month()
pl.col("date").dt.day()
pl.col("date").dt.hour()
pl.col("date").dt.minute()
pl.col("date").dt.second()
pl.col("date").dt.weekday()       # Monday=1, Sunday=7
pl.col("date").dt.ordinal_day()   # day of year (1-366)
pl.col("date").dt.week()          # ISO week number

# Format to string
pl.col("date").dt.strftime("%Y-%m-%d")
pl.col("date").dt.strftime("%B %d, %Y")

# Truncate (floor to interval)
pl.col("timestamp").dt.truncate("1h")    # truncate to hour
pl.col("timestamp").dt.truncate("1d")    # truncate to day
pl.col("timestamp").dt.truncate("1mo")   # truncate to month
pl.col("timestamp").dt.truncate("1w")    # truncate to week

# Round
pl.col("timestamp").dt.round("15m")

# Date arithmetic (use pl.duration)
pl.col("date") + pl.duration(days=7)
pl.col("date") - pl.duration(hours=3)

# Difference between dates
(pl.col("end") - pl.col("start")).dt.total_days()
(pl.col("end") - pl.col("start")).dt.total_hours()
(pl.col("end") - pl.col("start")).dt.total_seconds()

# Timezone handling
pl.col("ts").dt.replace_time_zone("UTC")
pl.col("ts").dt.convert_time_zone("America/New_York")
pl.col("ts").dt.replace_time_zone(None)  # strip timezone

# Parse string to date
pl.col("date_str").str.to_date("%Y-%m-%d")
pl.col("ts_str").str.to_datetime("%Y-%m-%d %H:%M:%S")
```

## List Operations (`.list`)

```python
# Length
pl.col("items").list.len()

# Get element by index
pl.col("items").list.get(0)         # first element
pl.col("items").list.get(-1)        # last element
pl.col("items").list.first()
pl.col("items").list.last()

# Contains
pl.col("tags").list.contains("python")

# Aggregation
pl.col("scores").list.sum()
pl.col("scores").list.mean()
pl.col("scores").list.max()
pl.col("scores").list.min()

# Join to string
pl.col("tags").list.join(", ")

# Slice
pl.col("items").list.slice(1, 3)    # start=1, length=3
pl.col("items").list.head(3)
pl.col("items").list.tail(3)

# Sort
pl.col("scores").list.sort()
pl.col("scores").list.sort(descending=True)
pl.col("scores").list.reverse()

# Unique values
pl.col("tags").list.unique()

# Explode (list to rows)
df.explode("tags")

# Eval — run an expression on each list
pl.col("values").list.eval(pl.element() * 2)
pl.col("prices").list.eval(pl.element().filter(pl.element() > 10))
```

## Struct Operations (`.struct`)

```python
# Access field
pl.col("address").struct.field("city")

# Multiple fields
pl.col("address").struct.field("city", "state")

# Unnest — expand struct into separate columns
df.unnest("address")

# Create struct from columns
df.select(
    pl.struct("name", "age").alias("person"),
)

# Rename fields
pl.col("person").struct.rename_fields(["full_name", "years"])
```

## Type Casting

```python
# Numeric conversions
pl.col("value").cast(pl.Float64)
pl.col("value").cast(pl.Int32)
pl.col("count").cast(pl.UInt32)

# Strict vs non-strict
pl.col("value").cast(pl.Int64, strict=False)  # returns null on failure

# String to numeric
pl.col("price_str").cast(pl.Float64)

# String to date/datetime
pl.col("date_str").str.to_date("%Y-%m-%d")
pl.col("ts_str").str.to_datetime("%Y-%m-%dT%H:%M:%S")

# Boolean
pl.col("flag").cast(pl.Boolean)

# Categorical (for low-cardinality strings — faster groupby/join)
pl.col("category").cast(pl.Categorical)

# Enum (known set of values — even faster, validates membership)
dtype = pl.Enum(["A", "B", "C"])
pl.col("grade").cast(dtype)

# Shrink dtype to smallest fitting type
df.select(pl.all().shrink_dtype())
```

## Null and NaN Handling

### Null vs NaN

Polars distinguishes between null (missing data) and NaN (IEEE 754 not-a-number). Most operations handle null natively. NaN only appears in Float columns and propagates in arithmetic.

```python
# Check for null
pl.col("value").is_null()
pl.col("value").is_not_null()

# Check for NaN
pl.col("value").is_nan()
pl.col("value").is_not_nan()

# Fill null
pl.col("value").fill_null(0)
pl.col("value").fill_null(pl.lit("unknown"))
pl.col("value").fill_null(strategy="forward")   # forward fill
pl.col("value").fill_null(strategy="backward")  # backward fill
pl.col("value").fill_null(strategy="mean")
pl.col("value").fill_null(strategy="min")
pl.col("value").fill_null(strategy="max")

# Fill NaN (must handle separately from null)
pl.col("value").fill_nan(0)
pl.col("value").fill_nan(None)  # convert NaN to null

# Drop rows with nulls
df.drop_nulls()                        # any column
df.drop_nulls(subset=["col1", "col2"]) # specific columns

# Coalesce — first non-null across multiple columns
pl.coalesce("primary_email", "secondary_email", "fallback_email")

# Null count
pl.col("value").null_count()
```

## Performance Patterns

### Streaming for Large Datasets

```python
# Read + transform + write without full materialization
(
    pl.scan_parquet("large_data/**/*.parquet")
    .filter(pl.col("date") >= "2024-01-01")
    .group_by("category")
    .agg(pl.col("revenue").sum())
    .collect(streaming=True)
)

# Sink directly to file
(
    pl.scan_csv("huge.csv")
    .filter(pl.col("active") == True)
    .sink_parquet("filtered.parquet")
)
```

### Memory Optimization

```python
# Use categorical for low-cardinality string columns
df = df.with_columns(
    pl.col("status").cast(pl.Categorical),
    pl.col("country").cast(pl.Categorical),
)

# Shrink numeric dtypes to smallest sufficient type
df = df.select(pl.all().shrink_dtype())

# Rechunk for contiguous memory after many operations
df = df.rechunk()
```

### Expression Parallelism

```python
# Polars automatically parallelizes independent expressions.
# Batch multiple column operations into a single context for best performance.

# Good — one context, parallel execution
df.with_columns(
    pl.col("a").sum().alias("sum_a"),
    pl.col("b").mean().alias("mean_b"),
    pl.col("c").std().alias("std_c"),
)

# Bad — three contexts, sequential execution
df = df.with_columns(pl.col("a").sum().alias("sum_a"))
df = df.with_columns(pl.col("b").mean().alias("mean_b"))
df = df.with_columns(pl.col("c").std().alias("std_c"))
```

### Predicate and Projection Pushdown

```python
# The optimizer pushes filters and column selections down to the scan.
# This means only necessary data is read from disk.

# Polars automatically optimizes this:
(
    pl.scan_parquet("data.parquet")
    .select("name", "revenue")                # projection pushdown
    .filter(pl.col("revenue") > 1000)         # predicate pushdown
    .collect()
)
# Only "name" and "revenue" columns are read; rows with revenue <= 1000 are skipped at I/O level.

# Verify with explain()
print(
    pl.scan_parquet("data.parquet")
    .select("name", "revenue")
    .filter(pl.col("revenue") > 1000)
    .explain()
)
```

## pandas-to-Polars Migration

Common operations side-by-side:

| Operation | pandas | Polars |
|---|---|---|
| Read CSV | `pd.read_csv("f.csv")` | `pl.read_csv("f.csv")` or `pl.scan_csv("f.csv")` |
| Select columns | `df[["a", "b"]]` | `df.select("a", "b")` |
| Filter rows | `df[df["a"] > 5]` | `df.filter(pl.col("a") > 5)` |
| Add column | `df["new"] = df["a"] + 1` | `df.with_columns((pl.col("a") + 1).alias("new"))` |
| Rename | `df.rename(columns={"a": "b"})` | `df.rename({"a": "b"})` |
| Sort | `df.sort_values("a")` | `df.sort("a")` |
| Group agg | `df.groupby("a").agg({"b": "sum"})` | `df.group_by("a").agg(pl.col("b").sum())` |
| Value counts | `df["a"].value_counts()` | `df["a"].value_counts()` |
| Unique values | `df["a"].unique()` | `df["a"].unique()` |
| Drop duplicates | `df.drop_duplicates(subset=["a"])` | `df.unique(subset=["a"])` |
| Null check | `df["a"].isna()` | `pl.col("a").is_null()` |
| Fill null | `df["a"].fillna(0)` | `pl.col("a").fill_null(0)` |
| Apply function | `df["a"].apply(fn)` | `pl.col("a").map_elements(fn)` (avoid if possible) |
| String methods | `df["a"].str.lower()` | `pl.col("a").str.to_lowercase()` |
| Date extraction | `df["d"].dt.year` | `pl.col("d").dt.year()` (note parentheses) |
| Pivot wider | `df.pivot_table(...)` | `df.pivot(on=..., values=...)` |
| Melt/unpivot | `pd.melt(df, ...)` | `df.unpivot(on=..., index=...)` |
| Concat | `pd.concat([df1, df2])` | `pl.concat([df1, df2])` |
| Merge/join | `pd.merge(df1, df2, on="a")` | `df1.join(df2, on="a")` |
| Reset index | `df.reset_index()` | N/A — Polars has no index |
| Set index | `df.set_index("a")` | N/A — Polars has no index |
| iterrows | `for _, row in df.iterrows()` | `for row in df.iter_rows(named=True)` (avoid if possible) |
