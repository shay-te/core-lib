---
id: function_utils
title: Function Utilities
sidebar: core_lib_doc_sidebar
permalink: function_utils.html
folder: core_lib_doc
toc: false
---

Helpers that read a function call's arguments by parameter name and fill a string template with them. Core-Lib's decorators use them to build cache keys, log lines and error messages from the decorated function's arguments.

> **Optional utility.** You rarely call these yourself. The one you are likely to use directly is `Keyable`, to control how your own objects appear in cache keys and log lines. The others are here for writing your own decorators.
>
> **Where it fits:** Decorator plumbing. `@Cache`, `@Logging`, `@NotFoundErrorHandler` and `@DuplicateErrorHandler` build their keys and messages with `build_function_key()`; `@Observe` and `@ParameterRuleValidator` find arguments by name with `get_func_parameter_index_by_name()`, and `@Observe` also uses `get_func_parameters_as_dict()`.

## Functions

### build_function_key()

*core_lib.helpers.func_utils.build_function_key()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/func_utils.py#L64){:target="_blank"}

Builds a string key from a template and the arguments passed to a function.

```python
def build_function_key(key: str, func, *args, **kwargs) -> str:
    ...
```

**Arguments**

- **`key`** *`(str)`*: Template with parameter names in braces, e.g. `'user_{user_id}'`. When empty, the function's `__qualname__` is returned.
- **`func`**: Function from which we wish to extract the parameters.
- __`*args, **kwargs`__: The function's args/kwargs for building the result string.


**Returns**

*`(str)`*: Returns a formatted key.

**Example**

```python
from core_lib.helpers.func_utils import build_function_key


def function_to_format(param_1, param_2, param_3="hello"):
    return None


formatted_parameters = build_function_key('key_{param_1}_{param_2}_{param_3}', function_to_format, 1, 2, "hello world")
print(formatted_parameters)  # key_1_2_hello world

formatted_parameters = build_function_key('key_{param_1}_{param_2}_{param_3}', function_to_format, 1)
print(formatted_parameters)  # key_1_!Eparam_2E!_hello
```
> **Note:** If a parameter's value is falsy (`0`, `''`, `None`), which includes a parameter that was not passed and has no default, it appears in the key as `!E<param_name>E!`. A name in the template that is not a parameter of the function appears as `!M<name>M!`. Newlines are removed from the result.

### get_func_parameters_as_dict()

*core_lib.helpers.func_utils.get_func_parameters_as_dict()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/func_utils.py#L47){:target="_blank"}

Extracts a function call into a dict where each key is a parameter name and each value is the argument value, default value, or `None`.

```python
def get_func_parameters_as_dict(func, *args, **kwargs) -> dict:
    ...
```

**Arguments**

- **`func`**: Function from which we wish to extract a parameter.
- __`*args, **kwargs`__: The function's args/kwargs for building the result string.


**Returns**

*`(dict)`*: Returns a dictionary with the parameter's name and value as key-value pair.

**Example**

```python
from core_lib.helpers.func_utils import get_func_parameters_as_dict

def function_to_extract(param_1: int, param_2: str, param_3 = "hello"):
    return None

extracted_dict = get_func_parameters_as_dict(function_to_extract) 
print(extracted_dict)  # {'param_1': None, 'param_2': None, 'param_3': 'hello'}

extracted_dict = get_func_parameters_as_dict(function_to_extract, 1, "hello", "world") 
print(extracted_dict)  # {'param_1': 1, 'param_2': 'hello', 'param_3': 'world'}
```
> **Note:** Will return the value as `None` if the parameter's value is missing.


### get_func_parameter_index_by_name()

*core_lib.helpers.func_utils.get_func_parameter_index_by_name()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/func_utils.py#L9){:target="_blank"}

Returns the zero-based position of a named parameter in a function signature.

```python
def get_func_parameter_index_by_name(func, parameter_name: str) -> int:
    ...
```

**Arguments**

- **`func`**: Function to which the parameter belongs.
- **`parameter_name`** *`(str)`*: The parameter's name from the function.


**Returns**

*`(int)`*: Returns the index of the parameter.

**Example**

```python
from core_lib.helpers.func_utils import get_func_parameter_index_by_name

def function_to_get_param_index(param_1, param_2):
    return None

parameter_index = get_func_parameter_index_by_name(function_to_get_param_index, "param_1") 
print(parameter_index) # 0

parameter_index = get_func_parameter_index_by_name(function_to_get_param_index, "param_2")
print(parameter_index) # 1
```
> **Note:** Raises `ValueError` if the function has no parameter with that name.


### Keyable Class

*core_lib.helpers.func_utils.Keyable* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/func_utils.py#L19){:target="_blank"}

`Keyable` lets an object control how it appears inside `build_function_key()`. Implement `key()` and return the safe, stable string you want in cache keys or log messages.

**Example**
```python
from core_lib.helpers.func_utils import Keyable, build_function_key

class User(Keyable):

    def __init__(self, u_id, name, details):
        self.id = u_id
        self.name = name
        self.details = details

    def key(self) -> str:
        return f'User(id:{self.id}, name:{self.name})'

def function_to_format(custom_key):
    return None

        
formatted_parameters = build_function_key('{custom_key}', function_to_format, User(4, 'Rosa Doe', None))
print(formatted_parameters)  # User(id:4, name:Rosa Doe)
```

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="files.html">Previous</a></button>
    <button class="pageNext-btn"><a href="generate_data.html">Next</a></button>
</div>
