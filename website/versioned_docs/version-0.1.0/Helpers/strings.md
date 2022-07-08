---
id: strings
title: String Helpers
sidebar_label: String Helpers
---

# String Helpers 

In string helpers we have functions that will convert different naming conventions.

## Functions

### snake_to_camel()

*core_lib.helpers.string.snake_to_camel()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/string.py#L4)

Will convert snake case to camel case.

```python
def snake_to_camel(snake_str) -> str:
```

**Arguments**

- **`snake_str`** *`(str)`*: Snake case string.

**Returns**

*`(str)`*: Return camel case string .

**Example**

```python
from core_lib.helpers.string import snake_to_camel

camel_case = snake_to_camel("this_is_snake_to_camel")
print(camel_case) # "ThisIsSnakeToCamel"
```

### camel_to_snake()

*core_lib.helpers.string.camel_to_snake()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/string.py#L8)

Will convert camel case to snake case.

```python
def camel_to_snake(s) -> str:
```

**Arguments**

- **`s`** *`(str)`*: Camel case string.

**Returns**

*`(str)`*: Return snake case string .

**Example**

```python
from core_lib.helpers.string import camel_to_snake

snake_case = camel_to_snake("ThisIsCamelToSnake")
print(snake_case) # "this_is_camel_to_snake"
```

### any_to_pascal()

*core_lib.helpers.string.any_to_pascal()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/string.py#L12)

Will convert any string to pascal case.

```python
def any_to_pascal(string: str) -> str:
```

**Arguments**

- **`string`** *`(str)`*: String to convert.

**Returns**

*`(str)`*: Return pascal case string.

**Example**

```python
from core_lib.helpers.string import any_to_pascal

pascal_case = any_to_pascal("this_is_pascal")
print(pascal_case) # "ThisIsPascal"
```