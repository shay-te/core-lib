---
id: result_to_dict
title: Result to Dict
sidebar: core_lib_doc_sidebar
permalink: result_to_dict.html
folder: core_lib_doc
toc: false
---
`@ResultToDict()` decorator transforms any value returned from the decorated function to a `dict` using the `result_to_dict` utility function.

### Example:

##### user_service.py

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

return any value passed into the `return_val` parameter as a `dict`

```python 
def result_to_dict(return_val, properties_as_dict: bool = True, callback: Callable[[dict], Awaitable[dict]] = None):
```

**Arguments**

- **`return_val`** *`(any)`*: Value to format.
- **`properties_as_dict`** *`(bool)`*: Default `True` , Will call `result_to_dict` for any property in the result `dict`.
- **`callback`** *`(Callable[[dict], Awaitable[dict]])`*: A custom callback for formatting nested objects.

**Returns**

A formatted `dict` transformation of the `return_val` parameter
For e.g., will return tuple as a tuple, dict as a dict

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

>For custom conversion, the `callback` function has to be implemented by the user for handling different types of data nested inside the given object.
> Also if the callback is not returning a new value, or it does not find any data to format it will return the original data.

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

# Nested data
data = {"apple", "cherry", {'fruit': 'kiwi', 'color': 'green', 'date': datetime.datetime.utcnow()}}
formatted_data = result_to_dict(data)
print(formatted_data)  # {"apple", "cherry", {'fruit': 'kiwi', 'color': 'green', 'date': '{timestamp of the datetime}'}

#Base/Database object
# query to select data from your DB
base_object = session.query(Data).all()

formatted_data = result_to_dict(base_object)
print(formatted_data) # {'id': 1, 'name': 'your_name', 'created_at':'11234322.6789', ...and other columns from your DB}

# Callback function for result_to_dict()
def convert_str_to_dict(result):
    data = result.get('additional_data')
    if data and isinstance(data, str):
        result['additional_data'] = json.loads(data)
    return result

# Callback implementation
data = {'name': 'Jon', 'email':'jon@mail.com', 'additional_data': '{"age": 42, "address": "Miami", "active": True}'}

# Callback will call the function and convert the json string inside the dict to object
formatted_data = result_to_dict(data, callback=convert_str_to_dict)
print(formatted_data) # {'name': 'Jon', 'email':'jon@mail.com', 'additional_data': {'age': 42, 'address': 'Miami', 'active': True}}

```

