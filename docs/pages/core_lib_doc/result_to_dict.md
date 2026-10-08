---
id: result_to_dict
title: Result to Dict
sidebar: core_lib_doc_sidebar
permalink: result_to_dict.html
folder: core_lib_doc
toc: false
---
`json.dumps` can't serialize SQLAlchemy entities, query `Row`s, datetimes, enums or `Decimal`s. `@ResultToDict()` converts what a Service method returns: entities and rows become dicts, and the datetimes, enums and `Decimal`s inside them become numbers. Anything it doesn't know is returned unchanged.

> **Where it fits:** Service-layer helper. Put `@ResultToDict()` on Service methods so callers (routes, jobs, tests) get plain dicts and lists, never ORM objects tied to a closed session.

## Example

### `user_service.py`

```python
from core_lib.data_layers.service.service import Service
from core_lib.data_transform.result_to_dict import ResultToDict
from your_core_lib.data_layers.data_access.user_data_access import UserDataAccess


class UserService(Service):
    def __init__(self, user_data_access: UserDataAccess):
        self._user_data_access = user_data_access

    @ResultToDict()
    def create(self, user_data: dict) -> dict:
        return self._user_data_access.create(user_data)

    @ResultToDict()
    def get(self, user_id: int) -> dict:
        return self._user_data_access.get(user_id)
```

If `UserDataAccess` is a [`CRUDDataAccess`](crud.html) over a `User` entity with `id`, `email`, an [`IntEnum`](sqlalchemy_types.html) `role` and a `created_at` datetime, `user_service.get(1)` returns a dict that `json.dumps` accepts:

```python
{'id': 1, 'email': 'jon@example.com', 'role': 1, 'created_at': 1715760000.0}
```

## What gets converted

| Returned value | Becomes |
|---|---|
| SQLAlchemy entity | A dict of its columns, plus relationships that are already loaded and any other attributes set on the instance. Each relationship is followed once per call, to avoid cycles. |
| `Row` from a column query, such as `session.query(User.id, User.email)` or a [JoinConfig](join_config.html) query | A dict keyed by column name or label. |
| Named tuple | A dict. |
| Dict | A dict with its values converted. |
| List | A list with each item converted. |
| Plain tuple | A tuple with each item converted by the value rules below (dicts inside it are not converted). |
| pymongo or mongomock cursor | A list of the documents, not converted further. |
| Anything else: sets, bytes, your own classes | Returned unchanged. `json.dumps` still fails on sets, bytes and custom objects. |

Values inside a dict, entity, `Row` or tuple:

| Value | Becomes |
|---|---|
| `enum.Enum` member | Its `.value`. |
| `datetime` | A float from `datetime.timestamp()`. A naive datetime is read in the server's local timezone. |
| `date` | The timestamp of midnight on that date, also a float. |
| `Decimal` | A float. |
| geoalchemy2 `WKBElement` (a `Geometry('POINT')` column) | `{'latitude': ..., 'longitude': ...}`, through [`Point.from_point_wkb()`](sqlalchemy_types.html#from_point_wkb). |
| A nested dict, list or entity, such as a JSON column | Converted by the same rules (unless `properties_as_dict=False`). |
| `int`, `float`, `str`, `bool`, `None`, `bytes` | Unchanged. |

> **Values are converted only inside a dict, entity, `Row` or tuple.** A datetime, enum or `Decimal` returned on its own, or sitting directly in a list, comes back unchanged: `result_to_dict(datetime(2024, 1, 1))` returns the datetime, and so does `result_to_dict({'when': [datetime(2024, 1, 1)]})['when'][0]`. Return a dict instead, such as `{'when': value}`.

## result_to_dict()

*core_lib.data_transform.result_to_dict.result_to_dict()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/data_transform/result_to_dict.py#L84){:target="_blank"}

Converts `return_val` by the rules above. `@ResultToDict()` calls it on the method's return value.

```python
def result_to_dict(return_val, properties_as_dict: bool = True, callback=None):
```

**Arguments**

- **`return_val`** *`(any)`*: Value to convert.
- **`properties_as_dict`** *`(bool)`*: Default `True`. When `True`, values inside the resulting dict that are not an `int`, `float`, `bool` or `str` (nested dicts, lists, entities) are converted too. When `False`, they are left as they are.
- **`callback`** *`(Callable[[Any], Any])`*: Optional. Called synchronously on the converted value at every level: the top-level result (unless it is a non-empty list), each list item, and each dict value that is not an `int`, `float`, `bool` or `str`, `None` included. Its return value replaces the value; if it returns `None` (or anything falsy), the value is kept. So it must accept any type: check `isinstance(value, dict)` first. (The source annotates it as `Callable[[dict], Awaitable[dict]]`, but it is never awaited.)

## ResultToDict

*core_lib.data_transform.result_to_dict.ResultToDict* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/data_transform/result_to_dict.py#L131){:target="_blank"}

The decorator form. `@ResultToDict(callback=...)` returns `result_to_dict(return_value, properties_as_dict=True, callback=callback)`.

```python
class ResultToDict(object):
    def __init__(self, callback=None):
```

## More examples

```python
import datetime
import enum
import json
from core_lib.data_transform.result_to_dict import result_to_dict


class Color(enum.Enum):
    RED = 1


# Lists and plain tuples keep their shape
print(result_to_dict([('fruit', 'apple'), ('fruit', 'banana')]))
# [('fruit', 'apple'), ('fruit', 'banana')]

# Enums and datetimes inside a dict become numbers (timestamp shown for a server in UTC)
print(result_to_dict(['apple', {'color': Color.RED, 'picked': datetime.datetime(2024, 1, 1)}]))
# ['apple', {'color': 1, 'picked': 1704067200.0}]

# A set, or a datetime on its own, comes back unchanged
print(result_to_dict({'apple', 'cherry'}))         # {'apple', 'cherry'}  (in some order)
print(result_to_dict(datetime.datetime(2024, 1, 1)))
# 2024-01-01 00:00:00


# A callback that parses a JSON string field. It also receives None, ints, list items...,
# so it returns anything that is not a dict untouched.
def parse_additional_data(value):
    if not isinstance(value, dict):
        return value
    additional_data = value.get('additional_data')
    if isinstance(additional_data, str):
        value['additional_data'] = json.loads(additional_data)
    return value


data = {'name': 'Jon', 'phone': None, 'additional_data': '{"age": 42, "active": true}'}
print(result_to_dict(data, callback=parse_additional_data))
# {'name': 'Jon', 'phone': None, 'additional_data': {'age': 42, 'active': True}}
```

With a SQLAlchemy session (`Data` is an entity with `id`, `name` and `created_at` columns):

```python
print(result_to_dict(session.query(Data).all()))
# [{'id': 1, 'name': 'your_name', 'created_at': 1715760000.0}]

print(result_to_dict(session.query(Data.id, Data.name).all()))
# [{'id': 1, 'name': 'your_name'}]
```

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="registry.html">Previous</a></button>
    <button class="pageNext-btn"><a href="rules_validator.html">Next</a></button>
</div>
