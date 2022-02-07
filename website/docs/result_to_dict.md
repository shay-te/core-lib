---
id: result_to_dict
title: Result to Dictionary
sidebar_label: Result to Dictionary
---
## result_to_dict() Function
Will format any value a function returns.
For e.g., will return tuple as a tuple, dict as a dict

Datatypes supported:

 - Point (Geographical point)
 - Varchar
 - ENUM
 - Integer
 - Test
 - JSON
 - BLOB/Binary
 - Boolean
 - Unicode
 - Float
 - Tuple
 - List
 - Dictionary
 - Set
 - Date
 - Datetime
 - Objects
 - Base
 > **Note:** Will convert `Date` and `Datetime` to timestamp.

 
### Usage

```python
import datetime
from core_lib.data_transform.result_to_dict import result_to_dict

# Tuples/List
data = [("fruit", "apple"), ("fruit", "banana"), ("fruit", "cherry")]
formatted_data = result_to_dict(data)
print(formatted_data)  # [("fruit", "apple"), ("fruit", "banana"), ("fruit", "cherry")]

# Sets/Objects
data = {"apple", "cherry"}
formatted_data = result_to_dict(data)
print(formatted_data)  # {"apple", "cherry"}

# Nested data
data = {"apple", "cherry", {'fruit': 'kiwi', 'color': 'green', 'date': datetime.datetime.utcnow()}}
formatted_data = result_to_dict(data)
print(formatted_data)  # {"apple", "cherry", {'fruit': 'kiwi', 'color': 'green', 'date': '{timestamp of the datetime}'}

```

## ResultToDict Decorator

The `ResultToDict` decorator uses `result_to_dict` function to carry out the formatting.

```python
class ResultToDict(object):
    
    def __init__(self, callback: Callable[[dict], Awaitable[dict]] = None):
        self.callback = callback

    def __call__(self, func, *args, **kwargs):

        @wraps(func)
        def __wrapper(*args, **kwargs):
            return_val = func(*args, **kwargs)
            return result_to_dict(return_val, properties_as_dict=True, callback=self.callback)
        return __wrapper

```
`func`: the decorated function that's returning the data.

`*args`, `**kwargs`: the args and kwargs of the decorated function.

`result_to_dict`: used by the decorator class to format the data

 
### Usage
```python
from core_lib.data_transform.result_to_dict import ResultToDict

@ResultToDict()
def format_data(self, param: tuple = ("apple", "orange")):
    return param

print(format_data()) # ("apple", "orange") 

print(format_data(("red", "blue"))) # ("red", "blue")
```