---
id: generate_data
title: Generate Data
sidebar: core_lib_doc_sidebar
permalink: generate_data.html
folder: core_lib_doc
toc: false
---

This helper provides functions that generate different types of data for us.

## Functions

### generate_random_string()

*core_lib.helpers.generate_data.generate_random_string()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/generate_data.py#L6){:target="_blank"}

Generates a random string of length `10` by default. Has options to add uppercase, numeric and special characters to the generated string too.

```python
def generate_random_string(length: int = 10, upper: bool = False, digits: bool = False, special: bool = False) -> str:
```

**Arguments**

- **`length`** *`(int)`*: Default `10`, Length of the generated string.
- **`upper`** *`(bool)`*: Default `False`, When `True` the string will include uppercase characters.
- **`digits`** *`(bool)`*: Default `False`, When `True` the string will include numeric digits characters.
- **`special`** *`(bool)`*: Default `False`, When `True` the string will include special characters or symbols.

**Returns**

*`(str)`*: A randomly generated string as configured in the function.

**Example**

```python
from core_lib.helpers.generate_data import generate_random_string

generate_random_string() # returns a string with length 10 and no uppercase, no digits and no special characters.
generate_random_string(10, True) # returns a string with length 10, includes uppercase and no digits and no special characters.
generate_random_string(10, True, True) # returns a string with length 10, includes uppercase and digits and no special characters.
generate_random_string(10, True, True, True) # returns a string with length 10, includes uppercase, digits and special characters.
```

### generate_email()

*core_lib.helpers.generate_data.generate_email()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/generate_data.py#L17){:target="_blank"}

Generates an Email with the provided domain name. The length of the Email ID name will be 10 characters.

```python
def generate_email(domain: str = 'domain.com') -> str:
```


**Arguments**

- **`domain`** *`(str)`*: Default `domain.com`, Domain name to be attached to the Email ID.

**Returns**

*`(str)`*: A randomly generated Email ID with the provided domain name and the length of the name will be `10`.

```python
from core_lib.helpers.generate_data import generate_email

generate_email() # returns an email id => qsrhbaykhg@domain.com
generate_email('core-lib.com') # returns an email id => qsrhbaykhg@core-lib.com
```

### generate_datetime()

*core_lib.helpers.generate_data.generate_datetime()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/generate_data.py#L21){:target="_blank"}

Generates a `datetime` within a specified range, if no range is provided the function will generate a `datetime` between `today - 10 days` and `today + 10 days` period.

```python
def generate_datetime(from_date: datetime = None, to_date: datetime = None) -> datetime:
```

**Arguments**

- **`from_date`** *`(datetime)`*: Default `None`, The `datetime` range to start from.
- **`to_date`** *`(datetime)`*: Default `None`, The `datetime` range to end with.

**Returns**

*`(datetime)`*: A randomly generated `datetime` within the given range.

```python
from core_lib.helpers.generate_data import generate_datetime
from datetime import datetime, timedelta

generate_datetime() # returns an datetime with from_date set to today - 10 days and to_date set to today + 10 days.
generate_datetime(datetime.today(), datetime.today() + timedelta(days=10)) # returns an email id => qsrhbaykhg@core-lib.com
```