---
id: datetime_utils
title: Datetime Utilities
sidebar_label: Datetime Utilities
---

## Datetime Utility Functions
Core-Lib has various datetime utility functions that returns `datetime` values in the `UTC` time.

### Functions
- `year_begin`
- `year_end`
- `month_begin`
- `month_end`
- `week_begin`
- `week_end`
- `day_begin`
- `day_end`
- `tomorrow`
- `yesterday`
- `midnight`
- `sunday`
- `monday`
- `tuesday`
- `wednesday`
- `thursday`
- `friday`
- `saturday`
- `hour_begin`
- `hour_end`

All the functions will return the values in `datetime` format. Functions for individual days will return the next coming
day of the week or next week for e.g., `friday` will return `datetime` of the friday occurring in this week or if not, 
then the next week.

### Usage
```python
    from core_lib.helpers.datetime_utils import year_begin 
    
    result = year_begin() # will return "2022-01-01 00:00:00"
```