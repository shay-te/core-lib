---
id: datetime_utils
title: Datetime Utilities
sidebar_label: Datetime Utilities
---

## Datetime Utility Functions
`Core-Lib` has various datetime utility functions that return `datetime` values in `UTC`. These functions will also set the returned value's `hour`, `minute`, `second` and `microsecond` to `0` where ever necessary.

### Functions
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


### Usage
```python
from core_lib.helpers.datetime_utils import year_begin 
    
beginning_of_the_year = year_begin() 
print(beginning_of_the_year) # will print "2022-01-01 00:00:00"
```