---
id: validation
title: Validation Helpers
sidebar: core_lib_doc_sidebar
permalink: validation.html
folder: core_lib_doc
toc: false
---

Small checks for values that often arrive as text, such as query-string parameters, form fields and config values. Most of them answer "**can this value be converted?**", not "is this already a Python `int`?" So `is_int('123')` is `True`, and so is `is_int(3.7)`. Each function below says exactly what it accepts.

> **Optional utility.** You can use Core-Lib without them. The `is_*` checks are a few lines over `int()`, `float()`, a string comparison, a regular expression or an `Enum` lookup, and return `False` instead of raising for a value that cannot be converted (`is_float()` notes an exception). The `is_email`/`is_url` checks expect a string or `None`. The `parse_*` helpers return lists and let conversion errors through. To check a whole dict of fields (allowed keys, types, custom rules) before it reaches a DataAccess, use the [Rule Validator](rules_validator.html) instead.
>
> **Where it fits:** Where you first read untrusted input: a web route or the Service method it calls.

## Functions

### is_bool()

*core_lib.helpers.validation.is_bool()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/validation.py#L12){:target="_blank"}

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

Returns `True` if `float(val)` succeeds. That includes ints, booleans, numeric strings such as `'1.5'` or `'1e3'`, and the strings `'nan'` and `'inf'`. Returns `False` for `None` and for strings that are not numbers. It can still raise for an `int` too large for a float: `is_float(10**400)` raises `OverflowError`, because only `ValueError` and `TypeError` are caught.

```python
def is_float(val) -> bool:
```

**Arguments**

- **`val`** *`(any)`*: Value to validate.

**Returns**

*`(bool)`*: `True` if `val` can be converted with `float()`.

**Example**

```python
from core_lib.helpers.validation import is_float

print(is_float(14.456))    # True
print(is_float('1.5'))     # True
print(is_float(14))        # True
print(is_float('string'))  # False
print(is_float(None))      # False
```

### is_int()

*core_lib.helpers.validation.is_int()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/validation.py#L28){:target="_blank"}

Returns `True` if `int(val)` succeeds. That includes ints, booleans, strings of digits such as `'123'`, and floats, which `int()` truncates (`is_int(3.7)` is `True`). Returns `False` for `None`, for strings that are not whole numbers (`'3.7'`, `'abc'`) and for infinity. If you need "is already an `int`", use `isinstance(val, int)`.

```python
def is_int(val) -> bool:
```

**Arguments**

- **`val`** *`(any)`*: Value to validate.

**Returns**

*`(bool)`*: `True` if `val` can be converted with `int()`.

**Example**

```python
from core_lib.helpers.validation import is_int

print(is_int(14))        # True
print(is_int('123'))     # True
print(is_int(3.7))       # True, int(3.7) is 3
print(is_int('3.7'))     # False
print(is_int('string'))  # False
```

### is_email()

*core_lib.helpers.validation.is_email()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/validation.py#L66){:target="_blank"}

Returns `True` if `email` matches a lightweight regular expression: something before `@`, then a domain that ends in a dot and at least two letters. It is a quick sanity check, not a full RFC 5322 validator: it accepts some invalid addresses (`'a b@x.com'`, with a space) and rejects some valid ones (`'user@localhost'`, no dot in the domain). Returns `False` for `None` or an empty string. Pass a string or `None`: a non-string such as `123` raises `TypeError`.

```python
def is_email(email: Optional[str]) -> bool:
```

**Arguments**

- **`email`** *`(str or None)`*: Value to validate.

**Returns**

*`(bool)`*: `True` if `email` matches the pattern.

**Example**

```python
from core_lib.helpers.validation import is_email

print(is_email('example.firstname-lastname@email.com'))  # True
print(is_email('<asd>>@strange.com'))                    # False
print(is_email(None))                                    # False
```

### is_int_enum()

*core_lib.helpers.validation.is_int_enum()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/validation.py#L72){:target="_blank"}

Returns `True` if `enum(int_value)` succeeds, that is, if `int_value` is the value of one of the members. Despite the name, it works for any `Enum`, including one with string values (`is_int_enum('red', Color)` is `True`). The value must match exactly: `'1'` is not `1`.

```python
def is_int_enum(int_value: Optional[int], enum: object) -> bool:
```

**Arguments**

- **`int_value`**: Value to look up.
- **`enum`** *`(Enum class)`*: The enum class to look it up in.

**Returns**

*`(bool)`*: `True` if `int_value` is a member's value.

**Example**

```python
from core_lib.helpers.validation import is_int_enum
import enum

class Status(enum.Enum):
    ACTIVE = 1
    BANNED = 2

print(is_int_enum(1, Status))    # True
print(is_int_enum(11, Status))   # False
print(is_int_enum('1', Status))  # False
```

### is_url()

*core_lib.helpers.validation.is_url()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/validation.py#L102){:target="_blank"}

Returns `True` for an `http://` or `https://` URL whose host is a domain name, `localhost` or an IPv4 address, with an optional port and path. Other schemes (`ftp://`, `mailto:`) and URLs without a scheme (`example.com`) return `False`, as do `None` and an empty string. Pass a string or `None`: a non-string such as `123` raises `TypeError`.

```python
def is_url(url: Optional[str]) -> bool:
```

**Arguments**

- **`url`** *`(str or None)`*: Value to validate.

**Returns**

*`(bool)`*: `True` if `url` matches the pattern.

**Example**

```python
from core_lib.helpers.validation import is_url

print(is_url('https://google.com'))          # True
print(is_url('http://localhost:8000/users'))  # True
print(is_url('ftp://example.com/file'))      # False
print(is_url('not a.url'))                   # False
```

### parse_comma_separated_list()

*core_lib.helpers.validation.parse_comma_separated_list()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/validation.py#L79){:target="_blank"}

Splits a comma-separated string into a list, strips whitespace around each item, drops empty items, and optionally applies a parser to each value. Returns an empty list for `None` or an empty string. If `value` is already a list it is passed through the same cleaning and parsing logic. An exception raised by `value_parser` is not caught.

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

print(parse_comma_separated_list('a, b, c'))       # ['a', 'b', 'c']
print(parse_comma_separated_list('1, 2, 3', int))  # [1, 2, 3]
print(parse_comma_separated_list('a,,b'))          # ['a', 'b']
print(parse_comma_separated_list(None))            # []
print(parse_comma_separated_list(''))              # []
```

### parse_int_list()

*core_lib.helpers.validation.parse_int_list()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/validation.py#L98){:target="_blank"}

Convenience wrapper around `parse_comma_separated_list` that converts each item to `int`. Use this when a query parameter or config value contains a comma-separated list of integers. If any item is not an integer, `int()` raises `ValueError`; in a web route, catch it and return a 400.

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

print(parse_int_list('1, 2, 3'))  # [1, 2, 3]
print(parse_int_list('42'))       # [42]
print(parse_int_list(None))       # []

try:
    parse_int_list('1, x')
except ValueError as error:
    print(error)  # invalid literal for int() with base 10: 'x'
```

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="strings.html">Previous</a></button>
    <button class="pageNext-btn"><a href="thread.html">Next</a></button>
</div>