---
id: validation
title: Validation Helpers
sidebar_label: Validation Helpers
---

## Validation Helpers
Here we have functions to validate the different datatypes and strings. Functions will return `boolean` values based on the validation.

### Functions and Usage

- `is_bool` will validate if the passed argument is type `boolean` or not.
    #### Usage
```python
from core_lib.helpers.validation import is_bool

print(is_bool(True)) # True
print(is_bool("true")) # True
print(is_bool("string")) # False
```

- `is_float` will validate if the passed argument is type `float` or not. 
    #### Usage
```python
from core_lib.helpers.validation import is_float

print(is_float(14.456)) # True
print(is_float("string")) # False
```

- `is_int` will validate if the passed argument is type `int` or not. 
    #### Usage
```python
from core_lib.helpers.validation import is_int

print(is_int(14)) # True
print(is_int("string")) # False
```

- `is_email` will validate if the passed string is a valid `email` or not. 
    #### Usage
```python
from core_lib.helpers.validation import is_email

print(is_email('example.firstname-lastname@email.com')) # True
print(is_email("<asd>>@strange.com")) # False
```

- `is_int_enum` will validate if the passed value is present in the `enum`. 
    #### Usage
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