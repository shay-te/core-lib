---
id: function_utils
title: Function Utilities
sidebar_label: Function Utilities
---

## Function Utils

These functions provide a unified way to retrieve or format a function's parameters
or get the calling module of a function.

### Functions and Usage

- `build_function_key` format a new string by merging a unique message with the function parameters and custom parameter.

```python
def build_function_key(key: str, func, *args, **kwargs) -> str:
    ....
```
`key`: base string for formatting the parameter, when not set the func.__qualname__ is used

`func`: the function to extract it parameter.

`*args`, `**kwargs`: the function args/kwargs for building the result string

#### Usage

```python
from core_lib.helpers.func_utils import build_function_key


def function_to_format(param_1, param_2, param_3="hello"):
    pass


formatted_parameters = build_function_key('key_{param_1}_{param_2}_{param_3}', function_to_format, 1, 2, "hello world")
print(formatted_parameters)  # key_1_2_hello world

formatted_parameters = build_function_key('key_{param_1}_{param_2}_{param_3}', function_to_format, 1)
print(formatted_parameters)  # key_1_!Eparam_2E!_hello
```
> **Note:** Will return `None` if the parameter's value is missing.



- `get_func_parameters_as_dict` extracts a function's parameters to `dict`, where key of the dictionary will be the parameter's name and value will be the value of the parameter.

```python
def get_func_parameters_as_dict(func, *args, **kwargs) -> dict:
    ....
```
`func`: the function to extract all of its parameters.

`*args`, `**kwargs`: the actual function args, kwargs.

#### Usage

```python
from core_lib.helpers.func_utils import get_func_parameters_as_dict

# A function that will take in 2 parameters one is type integer and other is string
def function_to_extract(param_1: int, param_2: str, param_3 = "hello"):
    pass

extracted_dict = get_func_parameters_as_dict(function_to_extract) 
print(extracted_dict)# {'param_1':None,'param_2':None, 'param_3':'hello'}

extracted_dict = get_func_parameters_as_dict(function_to_extract, 1, "hello", "world") 
print(extracted_dict)# {'param_1':'1', 'param_2':'hello', 'param_3':'world'}
```
> **Note:** Will return the value as `None` if the parameter's value is missing.



- `get_func_parameter_index_by_name` takes in a single parameter and function name and will return the parameter's index

```python
def get_func_parameter_index_by_name(func, parameter_name: str) -> int:
    ....
```
`func`: the function to which the parameters belong.

`parameter_name`: the name of the parameter from the function.

#### Usage
```python
from core_lib.helpers.func_utils import get_func_parameter_index_by_name

def function_to_get_param_index(param_1, param_2):
    pass

parameter_index = get_func_parameter_index_by_name(function_to_get_param_index, "param_1") 
print(function_to_get_param_index) # 0

parameter_index = get_func_parameter_index_by_name(function_to_get_param_index, "param_2")
print(function_to_get_param_index) # 1
```
> **Note:** Will raise an exception if the parameter passed is not valid



- `get_calling_module` will return the class and function names from wherever the function is being called.
    
    #### Usage
```python
from core_lib.helpers.func_utils import get_calling_module

result = get_calling_module(stack_depth=1)
```



- `reset_datetime` will reset the `hour`, `minute`, `second` and `microsecond` of a `datetime` value to `0`
    
    #### Usage

```python
import datetime
from core_lib.helpers.func_utils import reset_datetime

formatted_datetime = reset_datetime(datetime.datetime.utcnow())
print(formatted_datetime) #2022-02-07 00:00:00
```
