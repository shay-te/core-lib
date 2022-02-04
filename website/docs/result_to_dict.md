---
id: result_to_dict
title: Result to Dictionary
sidebar_label: Result to Dictionary
---
## ResultToDict Decorator

The `ResultToDict` decorator will format any value a function will return.
For eg. will return tuple as a tuple, dict as a dict.

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
from core_lib.data_transform.result_to_dict import ResultToDict

@ResultToDict()
def get_foo(self, param):
    return param
```
Will format what ever data the function is returning.

## result_to_dict() Function
Will do the same thing as the decorator but now can be used as a callable function instead of using the decorator.


 
### Usage
```python
from core_lib.data_transform.result_to_dict import result_to_dict

result = result_to_dict(data)
```
Will format what ever data the function is returning.

> **Note:** `@ResultToDict` decorator is also calling `result_to_dict()` to format the values