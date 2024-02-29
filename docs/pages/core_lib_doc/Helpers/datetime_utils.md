---
id: datetime_utils
title: Datetime Utilities
sidebar: core_lib_doc_sidebar
permalink: datetime_utils.html
folder: core_lib_doc
toc: false
---

*core_lib.helpers.datetime_utils* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/datetime_utils.py){:target="_blank"}

`Core-Lib` has various datetime utility functions that return `datetime` values in `UTC`. These functions will also set the returned value's `hour`, `minute`, `second` and `microsecond` to `0` where ever necessary.

## Functions
- `year_begin` returns the first day of the year.
- `year_end` returns date when current year will end.
- `month_begin` returns the first day of the current month.
- `month_end` returns the last day of the month.
- `week_begin` returns the first day of the week.
  >Note: The starting day of the week will be considered as Monday.
- `week_end` returns the last day of the week.
- `day_begin` returns the `datetime` for the beginning of the day.
- `day_end` returns the `datetime` for the ending of the day
- `tomorrow` returns tomorrow's day.
- `today` returns today's day.
- `yesterday` returns yesterday's day.
- `midnight` returns the midnight for today.
- `sunday` returns the next Sunday's date.
- `monday` returns the next Monday's date.
- `tuesday` returns the next Tuesday's date.
- `wednesday` returns the next Wednesday's date.
- `thursday` returns the next Thursday's date.
- `friday` returns the next Friday's date.
- `saturday` returns the next Saturday's date.
- `hour_begin` returns the time for the beginning of current hour.
- `hour_end` returns the time for the ending of current hour.
- `age` returns age in `int` for given `date`.
- `timestamp_to_ms` returns `timestamp` converted to `milliseconds`.


### Basic Usage
```python
from core_lib.helpers.datetime_utils import year_begin 
    
beginning_of_the_year = year_begin() 
print(beginning_of_the_year) # will print "2022-01-01 00:00:00"
```

### reset_datetime()

*core_lib.helpers.datetime_utils.reset_datetime()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/datetime_utils.py#L148){:target="_blank"}

Will reset the `hour`, `minute`, `second` and `microsecond` of a `datetime` value to `0`

```python
def reset_datetime(date: datetime):
```

**Arguments**

- **`date`** *`(datetime)`*: The DateTime to convert.


**Returns**

*`(datetime)`*: Returns the DateTime with `hour`, `minute`, `second` and `microsecond` as  `0`.

**Example**

```python
import datetime
from core_lib.helpers.datetime_utils import reset_datetime

formatted_datetime = reset_datetime(datetime.datetime.utcnow())
print(formatted_datetime) #2022-02-07 00:00:00
```

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/data_transform_helpers.html"><< Previous</a></button>
    <button class="pageNext-btn"><a href="/files.html">Next >></a></button>
</div>