---
id: datetime_utils
title: Datetime Utilities
sidebar: core_lib_doc_sidebar
permalink: datetime_utils.html
folder: core_lib_doc
toc: false
---

Functions that return the start or end of the current hour, day, week, month or year, and a few related helpers. They all work in **UTC** and return **naive** `datetime`s (no `tzinfo`), built from `datetime.utcnow()`.

> **Optional utility.** You can use Core-Lib without them; each is a line or two over `datetime` and `dateutil.relativedelta`. What they give you is one convention for date ranges across your code: UTC, and an end value that is the first moment of the **next** period.
>
> **Where it fits:** Usually a Service that builds date-range queries.

*core_lib.helpers.datetime_utils* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/datetime_utils.py){:target="_blank"}

## Functions

Each `*_end()` function returns the **first moment of the next period**, not the last day of this one: `month_end()` in October is November 1 at 00:00. Use it as an exclusive upper bound, `begin <= value < end`.

| Function | Returns (shown for Thursday 2026-10-08 15:42 UTC) |
|---|---|
| `year_begin()` | January 1 of this year, 00:00 (`2026-01-01 00:00`). |
| `year_end()` | January 1 of **next** year, 00:00 (`2027-01-01 00:00`). |
| `month_begin()` | Day 1 of this month, 00:00 (`2026-10-01 00:00`). |
| `month_end()` | Day 1 of **next** month, 00:00 (`2026-11-01 00:00`). |
| `week_begin()` | Monday of this week, 00:00 (`2026-10-05 00:00`). |
| `week_end()` | **Next** Monday, 00:00 (`2026-10-12 00:00`). |
| `day_begin()` | Today, 00:00 (`2026-10-08 00:00`). |
| `day_end()` | Tomorrow, 00:00 (`2026-10-09 00:00`). |
| `hour_begin()` | Start of this hour (`2026-10-08 15:00`). |
| `hour_end()` | Start of the next hour (`2026-10-08 16:00`). |
| `today()`, `midnight()` | Today at 00:00, as a `datetime`, not a `date` (`2026-10-08 00:00`). |
| `tomorrow()` | Tomorrow at 00:00 (`2026-10-09 00:00`). |
| `yesterday()` | Yesterday at 00:00 (`2026-10-07 00:00`). |
| `monday()` … `sunday()` | The next such weekday at 00:00, **never today**: on a Thursday, `thursday()` is next week's (`2026-10-15 00:00`), and `friday()` is tomorrow (`2026-10-09 00:00`). |
| `age(born)` | Whole years since the `date` `born`. It uses the local date (`date.today()`), not UTC. |
| `timestamp_to_ms(timestamp)` | A Unix timestamp in seconds converted to whole milliseconds, `int(timestamp * 1000)`. |

Every function in this table except `age()` and `timestamp_to_ms()` takes optional `hours=` and `minutes=` offsets that move the result within its day; `hour_begin()` and `hour_end()` take `minutes=` only. On the same Thursday, `day_begin(hours=9)` is `2026-10-08 09:00`, `day_end(hours=9)` is `2026-10-09 09:00`, and `hour_begin(minutes=30)` is `2026-10-08 15:30`.

## Example: this month's rows

```python
from core_lib.helpers.datetime_utils import day_begin, month_begin, month_end

start, end = month_begin(), month_end()
print(start, end)                  # e.g. 2026-10-01 00:00:00 2026-11-01 00:00:00
print(start <= day_begin() < end)  # True: today falls in this month's range

# In a SQLAlchemy query: .filter(Order.created_at >= start, Order.created_at < end)
```

## `reset_datetime()`

*core_lib.helpers.datetime_utils.reset_datetime()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/datetime_utils.py#L148){:target="_blank"}

Resets the `hour`, `minute`, `second`, and `microsecond` of a `datetime` value to `0`.

```python
def reset_datetime(date: datetime):
```

**Arguments**

- **`date`** *`(datetime)`*: The datetime to reset. Any `tzinfo` is kept.


**Returns**

*`(datetime)`*: Returns the datetime with `hour`, `minute`, `second` and `microsecond` set to `0`.

**Example**

```python
from datetime import datetime

from core_lib.helpers.datetime_utils import reset_datetime

print(reset_datetime(datetime(2026, 10, 8, 15, 42, 10)))  # 2026-10-08 00:00:00
```

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="data_transform_helpers.html">Previous</a></button>
    <button class="pageNext-btn"><a href="files.html">Next</a></button>
</div>