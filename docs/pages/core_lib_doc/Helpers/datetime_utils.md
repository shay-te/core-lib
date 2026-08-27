---
id: datetime_utils
title: Datetime Utilities
sidebar: core_lib_doc_sidebar
permalink: datetime_utils.html
folder: core_lib_doc
toc: false
---

Datetime bugs often come from inconsistent timezones and mismatched precision — comparing a datetime with a time component against one without silently returns the wrong result. These utilities always return UTC datetimes with sub-day components zeroed out, so date comparisons and range queries work predictably.

> **Where it fits:** Cross-cutting. Use in any layer that needs UTC-aligned date boundaries — typically Service code that builds date-range queries.

*core_lib.helpers.datetime_utils* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/datetime_utils.py){:target="_blank"}

## Functions

| Function | Returns |
|---|---|
| `year_begin()` | First day of the current year. |
| `year_end()` | Last day of the current year. |
| `month_begin()` | First day of the current month. |
| `month_end()` | Last day of the current month. |
| `week_begin()` | First day (Monday) of the current week. |
| `week_end()` | Last day (Sunday) of the current week. |
| `day_begin()` | Beginning of the current day. |
| `day_end()` | End of the current day. |
| `today()` | Today's date. |
| `tomorrow()` | Tomorrow's date. |
| `yesterday()` | Yesterday's date. |
| `midnight()` | Midnight of today. |
| `monday()` … `sunday()` | The next occurrence of that weekday. |
| `hour_begin()` | Beginning of the current hour. |
| `hour_end()` | End of the current hour. |
| `age(date)` | Age in years for the given `date`. |
| `timestamp_to_ms(ts)` | Timestamp converted to milliseconds. |

## Basic usage

```python
from core_lib.helpers.datetime_utils import year_begin

start = year_begin()
print(start)   # 2026-01-01 00:00:00
```

## `reset_datetime()`

*core_lib.helpers.datetime_utils.reset_datetime()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/datetime_utils.py#L148){:target="_blank"}

Resets the `hour`, `minute`, `second`, and `microsecond` of a `datetime` value to `0`.

```python
def reset_datetime(date: datetime):
```

**Arguments**

- **`date`** *`(datetime)`*: The datetime to convert.


**Returns**

*`(datetime)`*: Returns the datetime with `hour`, `minute`, `second` and `microsecond` set to `0`.

**Example**

```python
import datetime
from core_lib.helpers.datetime_utils import reset_datetime

formatted_datetime = reset_datetime(datetime.datetime.utcnow())
print(formatted_datetime) #2022-02-07 00:00:00
```

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/data_transform_helpers.html">Previous</a></button>
    <button class="pageNext-btn"><a href="/files.html">Next</a></button>
</div>