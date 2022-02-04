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

result = is_bool(True) # will return True
result = is_bool("true") # will return True
result = is_bool("string") # will return False
```

- `is_float` will validate if the passed argument is type `float` or not. 
    #### Usage
```python
from core_lib.helpers.validation import is_float

result = is_float(14.456) # will return True
result = is_float("string") # will return False
```

- `is_int` will validate if the passed argument is type `int` or not. 
    #### Usage
```python
from core_lib.helpers.validation import is_int

result = is_int(14) # will return True
result = is_int("string") # will return False
```

- `is_email` will validate if the passed string is a valid `email` or not. 
    #### Usage
```python
from core_lib.helpers.validation import is_email

result = is_email('example.firstname-lastname@email.com') # will return True
result = is_email("<asd>>@strange.com") # will return False
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

result = is_int_enum(MyEnum.one.value, MyEnum) # will return True
result = is_int_enum(11, MyEnum) # will return False
```