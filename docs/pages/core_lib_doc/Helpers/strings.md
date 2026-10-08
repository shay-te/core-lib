---
id: strings
title: String Helpers
sidebar: core_lib_doc_sidebar
permalink: strings.html
folder: core_lib_doc
toc: false
---

Three small converters between naming styles. Core-Lib's [code generator](generation.html) uses them to turn a name like `user_core_lib` into a class name like `UserCoreLib`, and back into module names.

> **Optional utility.** You can use Core-Lib without them. They are built for **class and module names**, not for JSON field names: `snake_to_camel` produces **PascalCase** (`user_id` → `UserId`), not the `userId` style most JSON APIs use.
>
> **Where it fits:** Code that generates or looks up classes and modules by name.

## Functions

### snake_to_camel()

*core_lib.helpers.string.snake_to_camel()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/string.py#L4){:target="_blank"}

Converts `snake_case` to `PascalCase`: every word is capitalised, including the first. Other letters are lowercased (`USER_ID` → `UserId`).

```python
def snake_to_camel(snake_str) -> str:
```

**Arguments**

- **`snake_str`** *`(str)`*: Snake case string.

**Returns**

*`(str)`*: The PascalCase string.

**Example**

```python
from core_lib.helpers.string import snake_to_camel

print(snake_to_camel('user_core_lib'))  # UserCoreLib
print(snake_to_camel('user_id'))        # UserId
```

### camel_to_snake()

*core_lib.helpers.string.camel_to_snake()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/string.py#L8){:target="_blank"}

Converts `PascalCase` or `camelCase` to `snake_case` by putting `_` before every capital letter. Runs of capitals are split letter by letter: `HTTPServer` becomes `h_t_t_p_server`.

```python
def camel_to_snake(s) -> str:
```

**Arguments**

- **`s`** *`(str)`*: PascalCase or camelCase string.

**Returns**

*`(str)`*: The snake_case string.

**Example**

```python
from core_lib.helpers.string import camel_to_snake

print(camel_to_snake('UserCoreLib'))  # user_core_lib
print(camel_to_snake('userId'))       # user_id
print(camel_to_snake('HTTPServer'))   # h_t_t_p_server
```

### any_to_pascal()

*core_lib.helpers.string.any_to_pascal()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/string.py#L12){:target="_blank"}

Converts a string to `PascalCase`. It splits on any character that is not a letter or digit (`_`, `-`, space, `.`), capitalises the first letter of each part and keeps the rest of each part as it is, so `userCoreLib` becomes `UserCoreLib`. A leading digit is dropped (`1st_place` → `StPlace`). An empty string raises `IndexError`.

```python
def any_to_pascal(string: str) -> str:
```

**Arguments**

- **`string`** *`(str)`*: String to convert.

**Returns**

*`(str)`*: The PascalCase string.

**Example**

```python
from core_lib.helpers.string import any_to_pascal

print(any_to_pascal('user_core_lib'))  # UserCoreLib
print(any_to_pascal('user-core lib'))  # UserCoreLib
print(any_to_pascal('userCoreLib'))    # UserCoreLib
```

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="logger.html">Previous</a></button>
    <button class="pageNext-btn"><a href="validation.html">Next</a></button>
</div>