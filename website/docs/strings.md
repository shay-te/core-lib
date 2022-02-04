---
id: strings
title: String Helpers
sidebar_label: String Helpers
---

## String Helpers 

In string helpers we have functions that will convert different naming conventions.

### Functions and Usage

- `snake_to_camel` will convert snake case to camel case.
- `camel_to_snake` will convert camel case to snake case.
    #### Usage
```python
from core_lib.helpers.string import snake_to_camel, camel_to_snake

def foo(param_1, param_2):
    pass

result = snake_to_camel("this_is_snake_to_camel") # will return "ThisIsSnakeToCamel"
result = camel_to_snake("ThisIsCamelToSnake") # will return "this_is_camel_to_snake"
```