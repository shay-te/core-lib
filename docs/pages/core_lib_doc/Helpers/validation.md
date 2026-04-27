---
id: validation
title: Validation Helpers
sidebar: core_lib_doc_sidebar
permalink: validation.html
folder: core_lib_doc
toc: false
---

Validating input types is trickier than it looks — a string `"true"` isn't a Python `bool`, a string `"123"` isn't an `int`, and checking enum membership requires iterating values. These helpers handle the common edge cases and return a clean `bool`, so your validation logic stays simple.

## Functions

### is_bool()

*core_lib.helpers.validation.is_bool()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/validation.py#L10){:target="_blank"}

Returns `True` if the value is a Python `bool`, or the string `"true"` / `"false"` (case-insensitive). Returns `False` for anything else.

```python
def is_bool(val) -> bool:
```

**Arguments**

- **`val`** *`(any)`*: Value to validate.

**Returns**

*`(bool)`*: `True` if `val` is a boolean or a boolean-like string; `False` otherwise.

**Example**

```python
from core_lib.helpers.validation import is_bool

print(is_bool(True))      # True
print(is_bool(False))     # True
print(is_bool("true"))    # True
print(is_bool("false"))   # True
print(is_bool("string"))  # False
print(is_bool(1))         # False
```

### is_float()

*core_lib.helpers.validation.is_float()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/validation.py#L18){:target="_blank"}

Will validate if the passed argument is type `float` or not. 

```python
def is_float(val) -> bool:
```

**Arguments**

- **`val`** *`(any)`*: Value to validate.

**Returns**

*`(bool)`*: Return True or False based upon the validation.

**Example**

```python
from core_lib.helpers.validation import is_float

print(is_float(14.456)) # True
print(is_float("string")) # False
```

### is_int()

*core_lib.helpers.validation.is_int()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/validation.py#L28){:target="_blank"}

Will validate if the passed argument is type `int` or not. 

```python
def is_int(val) -> bool:
```

**Arguments**

- **`val`** *`(any)`*: Value to validate.

**Returns**

*`(bool)`*: Return True or False based upon the validation.

**Example**

```python
from core_lib.helpers.validation import is_int

print(is_int(14)) # True
print(is_int("string")) # False
```

### is_email()

*core_lib.helpers.validation.is_email()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/validation.py#L41){:target="_blank"}

Will validate if the passed string is a valid `email` or not. 

```python
def is_email(email: str) -> bool:
```

**Arguments**

- **`email`** *`(str)`*: Value to validate.

**Returns**

*`(bool)`*: Return True or False based upon the validation.

**Example**

```python
from core_lib.helpers.validation import is_email

print(is_email('example.firstname-lastname@email.com')) # True
print(is_email("<asd>>@strange.com")) # False
```

### is_int_enum()

*core_lib.helpers.validation.is_int_enum()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/validation.py#L48){:target="_blank"}

Will validate if the passed value is present in the `enum`. 


```python
def is_int_enum(int_value: int, enum: IntEnum) -> bool:
```

**Arguments**

- **`int_value`** *`(int)`*: Value to validate.
- **`enum`** *`(IntEnum)`*: Enum class to validate from.

**Returns**

*`(bool)`*: Return True or False based upon the validation.

**Example**

```python
from core_lib.helpers.validation import is_int_enum
import enum

class MyEnum(enum.Enum):
    one = 1
    two = 2
    three = 3

print(is_int_enum(MyEnum.one.value, MyEnum)) # True
print(is_int_enum(11, MyEnum)) # False
```

### is_url()

*core_lib.helpers.validation.is_url()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/validation.py#L55){:target="_blank"}

Will validate if the passed value is an `url`. 


```python
def is_url(url: str) -> bool:
```

**Arguments**

- **`url`** *`(str)`*: Value to validate.

**Returns**

*`(bool)`*: Return True or False based upon the validation.

**Example**

```python
from core_lib.helpers.validation import is_url

print(is_url('https://google.com')) # True
print(is_url('not a.url')) # False
```

### parse_comma_separated_list()

*core_lib.helpers.validation.parse_comma_separated_list()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/validation.py#L79){:target="_blank"}

Splits a comma-separated string into a list, strips whitespace around each item, and optionally applies a parser to each value. Returns an empty list for `None` or an empty string. If `value` is already a list it is passed through the same cleaning and parsing logic.

```python
def parse_comma_separated_list(value, value_parser: Optional[Callable[[str], ParsedValue]] = None) -> list:
```

**Arguments**

- **`value`** *`(str | list | None)`*: A comma-separated string, an existing list, or `None`.
- **`value_parser`** *`(Callable, optional)`*: A callable applied to each cleaned item. Defaults to identity (items returned as strings).

**Returns**

*`(list)`*: Parsed list of values.

**Example**

```python
from core_lib.helpers.validation import parse_comma_separated_list

parse_comma_separated_list("a, b, c")           # ['a', 'b', 'c']
parse_comma_separated_list("1, 2, 3", int)      # [1, 2, 3]
parse_comma_separated_list(None)                 # []
parse_comma_separated_list("")                   # []
```

### parse_int_list()

*core_lib.helpers.validation.parse_int_list()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/validation.py#L98){:target="_blank"}

Convenience wrapper around `parse_comma_separated_list` that converts each item to `int`. Use this when a query parameter or config value contains a comma-separated list of integers.

```python
def parse_int_list(value) -> list:
```

**Arguments**

- **`value`** *`(str | list | None)`*: A comma-separated string of integers, an existing list, or `None`.

**Returns**

*`(list)`*: List of `int` values.

**Example**

```python
from core_lib.helpers.validation import parse_int_list

parse_int_list("1, 2, 3")   # [1, 2, 3]
parse_int_list("42")         # [42]
parse_int_list(None)          # []
```

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/strings.html"><< Previous</a></button>
    <button class="pageNext-btn"><a href="/thread.html">Next >></a></button>
</div>