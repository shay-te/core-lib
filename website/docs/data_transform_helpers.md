---
id: data_transform_helpers
title: Data Transform Helpers
sidebar_label: Data Transform Helpers
---

# Data Transform Helpers
Provides functions for reading and manipulating `dict`.

## Functions

#### get_dict_attr()
From the dictionary, returns the value for the given path.

```python
def get_dict_attr(obj: dict, path: str):
```

`obj` (*dict*): `dict` to read.

`path` (*str*): The path to read the value from.

#### set_dict_attr()
Sets the value of a path-described object. It will be created if any section of the object path does not exist.

```python
def set_dict_attr(obj: dict, path: str, value) -> dict:
```

`obj` (*dict*): `dict` to update.

`path` (*str*): The path to which the value should be set.

`value` (*value*): The value to be set at the target path.

## Example

```python
from core_lib.data_transform.helpers import get_dict_attr, set_dict_attr

data = {'name': 'Jon', 'education':{'school': 'Public School'}}

value = get_dict_attr(data, 'education.school')
print(value)  # Public School

value = get_dict_attr(data, 'name')
print(value)  # Jon

set_dict_attr(data, 'education.school', 'International School')
print(get_dict_attr(data, 'education.school')) # International School

new_data = set_dict_attr({}, '1.2.3', 'new dict')
print(new_data) # {'1':{'2':{'3': 'new dict'}}}
```

