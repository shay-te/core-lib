---
id: function_utils
title: Function Utilities
sidebar_label: Function Utilities
---

## Function Utility Functions

These functions provide a unified way to retrieve or format a function's parameters
or get the calling module of a function.

### Functions and Usage

- `build_value_by_func_parameters` this function accepts a `key` parameter in type `str` which contains the parameter's placeholders and then returns out the string by replacing the placeholders with the parameter's actual value.

    #### Usage
```python
from core_lib.helpers.func_utils import build_value_by_func_parameters

def foo(param_1, param_2):
    pass

result = build_value_by_func_parameters('key_{param_1}_{param_2}', foo, 1, 2) # will return key_1_2
result = build_value_by_func_parameters('key_{param_1}_{param_2}', foo, 1) # will return key_1_param_2
```
> **Note:** Will return the name of the placeholder if the parameter's value is missing.

- `get_func_parameters_as_dict` will return the function's parameters formatted as a `dict` where key of the dictionary will be the parameter's name and value will be the value of the parameter.
    
    #### Usage
```python
from core_lib.helpers.func_utils import get_func_parameters_as_dict

def foo(param_1, param_2):
    pass

result = get_func_parameters_as_dict(foo) # will return {'param_1':'param_1','param_2':'param_2'}
result = get_func_parameters_as_dict(foo, 1, 2) # will return {'param_1':'1','param_2':'2'}
```
> **Note:** Will return the value as the name of the parameter itself if the parameter's value is missing.

- `get_func_parameter_index_by_name` takes in a single parameter and function name and will return the parameter's index
    
    #### Usage
```python
from core_lib.helpers.func_utils import get_func_parameter_index_by_name

def foo(param_1, param_2):
    pass

result = get_func_parameter_index_by_name(foo, param_1) # will return 0
result = get_func_parameter_index_by_name(foo, param_2) # will return 1
```
> **Note:** Will raise an exception if the parameter passed is not valid

- `get_calling_module` will return the class and function names from wherever the function is being called.
    
    #### Usage
```python
from core_lib.helpers.func_utils import get_calling_module

result = get_calling_module(stack_depth=1)
```

- `reset_datetime` will reset the `hour`, `minute`, `second` and `microsecond` of a `datetime` value
    
    #### Usage
```python
from core_lib.helpers.func_utils import reset_datetime

result = reset_datetime(datetime_value) # will return the datetime with hour, minute, second and microsecond with 00
```
