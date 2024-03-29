---
id: validation
title: Validation Helpers
sidebar: core_lib_doc_sidebar
permalink: validation.html
folder: core_lib_doc
toc: false
---

Here we have functions to validate the different datatypes and strings. Functions will return `boolean` values based on the validation.

## Functions

### is_bool()

*core_lib.helpers.validation.is_bool()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/validation.py#L10){:target="_blank"}

Will validate if the passed argument is type `boolean` or not.

```python
def is_bool(val) -> bool:
```

**Arguments**

- **`val`** *`(any)`*: Value to validate.

**Returns**

*`(bool)`*: Return True or False based upon the validation.

**Example**

```python
from core_lib.helpers.validation import is_bool

print(is_bool(True)) # True
print(is_bool("true")) # True
print(is_bool("string")) # False
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

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/strings.html"><< Previous</a></button>
    <button class="pageNext-btn"><a href="/test_core_lib.html">Next >></a></button>
</div>