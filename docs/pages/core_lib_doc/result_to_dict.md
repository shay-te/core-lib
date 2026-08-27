---
id: result_to_dict
title: Result to Dict
sidebar: core_lib_doc_sidebar
permalink: result_to_dict.html
folder: core_lib_doc
toc: false
---
SQLAlchemy model objects, custom Python objects, and raw rows can't be serialized to JSON directly. `@ResultToDict()` automatically converts whatever your service returns into a plain dict — no manual per-field mapping needed.

> **Where it fits:** Service-layer helper. Apply `@ResultToDict()` to a Service method so its return value is JSON-serializable before the web layer hands it back.

## Example

### `user_service.py`

```python
from core_lib.data_transform.result_to_dict import ResultToDict

class UserService(Service):
    def __init__(self, data_access: UserDataAccess):
        self.data_access = data_access

    @ResultToDict()
    def create(self, user_data):
        return self.data_access.create(user_data)

    @ResultToDict()
    def get(self, user_id):
        return self.data_access.get(user_id)
```



### result_to_dict() Function

*core_lib.data_transform.result_to_dict.result_to_dict()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/data_transform/result_to_dict.py#L74){:target="_blank"}

Converts the value passed to `return_val` into JSON-friendly Python data.

```python 
def result_to_dict(return_val, properties_as_dict: bool = True, callback: Callable[[dict], Awaitable[dict]] = None):
```

**Arguments**

- **`return_val`** *`(any)`*: Value to format.
- **`properties_as_dict`** *`(bool)`*: Default `True` , Will call `result_to_dict` for any property in the result `dict`.
- **`callback`** *`(Callable[[dict], Awaitable[dict]])`*: A custom callback for formatting nested objects.

**Returns**

The converted value. Existing dicts stay dicts, tuples stay tuples, and objects are converted into dicts where possible.

### Datatypes supported

**Python**

 - Float
 - Tuple
 - List
 - Dictionary
 - Set
 - Binary
 - ENUM
 - Integer
 - String
 - Boolean
 - Unicode
 - Date ( converted to `timestamp` )
 - Datetime ( converted to `timestamp` )
 - Objects ( converted to `dict` )

**SQLAlchemy**

 - Varchar
 - ENUM
 - Integer
 - Float
 - Text
 - JSON ( converted to `dict` )
 - BLOB/Binary
 - Boolean
 - Unicode
 - Date ( converted to `timestamp` )
 - Datetime ( converted to `timestamp` )


### Example

> Implement `callback` when nested data needs custom conversion.
> If the callback does not return a new value, or finds nothing to format, the original data is returned.

```python
import datetime
import enum
import json
from geoalchemy2 import WKTElement
from core_lib.data_transform.result_to_dict import result_to_dict

class MyEnum(enum.Enum):
    one = 1
    two = 2
    three = 3
    
# Tuples/List
data = [("fruit", "apple"), ("fruit", "banana"), ("fruit", "cherry")]
formatted_data = result_to_dict(data)
print(formatted_data)  # [("fruit", "apple"), ("fruit", "banana"), ("fruit", "cherry")]

# Sets/Objects
data = {"apple", "cherry"}
formatted_data = result_to_dict(data)
print(formatted_data)  # {"apple", "cherry"}

# Nested data (lists can hold mixed types, including dicts)
data = ["apple", "cherry", {'fruit': 'kiwi', 'color': 'green', 'date': datetime.datetime.utcnow()}]
formatted_data = result_to_dict(data)
print(formatted_data)  # ["apple", "cherry", {'fruit': 'kiwi', 'color': 'green', 'date': '<timestamp of the datetime>'}]

# SQLAlchemy query result
base_object = session.query(Data).all()

formatted_data = result_to_dict(base_object)
print(formatted_data)  # {'id': 1, 'name': 'your_name', 'created_at': '<timestamp>', ...}

# Callback function for result_to_dict()
def convert_str_to_dict(result):
    data = result.get('additional_data')
    if data and isinstance(data, str):
        result['additional_data'] = json.loads(data)
    return result

# Callback implementation
data = {'name': 'Jon', 'email': 'jon@mail.com', 'additional_data': '{"age": 42, "address": "Miami", "active": true}'}

# Callback converts the JSON string inside the dict to an object.
formatted_data = result_to_dict(data, callback=convert_str_to_dict)
print(formatted_data)  # {'name': 'Jon', 'email': 'jon@mail.com', 'additional_data': {'age': 42, 'address': 'Miami', 'active': True}}

```

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/registry.html">Previous</a></button>
    <button class="pageNext-btn"><a href="/rules_validator.html">Next</a></button>
</div>
