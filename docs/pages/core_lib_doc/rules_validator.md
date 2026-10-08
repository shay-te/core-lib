---
id: rules_validator
title: Rules Validator
sidebar: core_lib_doc_sidebar
permalink: rules_validator.html
folder: core_lib_doc
toc: false
---

`RuleValidator` checks a `dict` of column values against a list of rules, one `ValueRuleValidator` per key, before the dict is written to the database. It converts what it safely can (the string `'180'` to the int `180`, `'1990-04-01'` to a `datetime`), and raises `PermissionError` for anything that breaks a rule. The one exception is an error raised inside your own `custom_converter`: it propagates unchanged (see `custom_converter` below).

> **Where it fits:** DataAccess layer. Pass a `RuleValidator` to a [CRUD base class](crud.html) and its `create()` and `update()` validate every dict. For your own DataAccess methods, use `@ParameterRuleValidator`.

## Example

### `user.py`

```python
from sqlalchemy import Column, Date, Integer, VARCHAR, BOOLEAN
from core_lib.data_layers.data.db.sqlalchemy.base import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(VARCHAR(length=255), nullable=False)
    agreement = Column(BOOLEAN(), default=False, nullable=False)
    height = Column(Integer)
    birthday = Column(Date)
```

### `user_data_access.py`

```python
import datetime

from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.data_layers.data_access.db.crud.crud_data_access import CRUDDataAccess
from core_lib.rule_validator.rule_validator import RuleValidator, ValueRuleValidator
from core_lib.rule_validator.rule_validator_decorator import ParameterRuleValidator
from your_core_lib.data_layers.data.db.entities.user import User

user_rule_validator = RuleValidator([
    ValueRuleValidator(User.email.key, str),
    ValueRuleValidator(User.agreement.key, bool),
    ValueRuleValidator(User.height.key, int, custom_validator=lambda height: height is None or height > 50),
    ValueRuleValidator(User.birthday.key, datetime.date),
])


class UserDataAccess(CRUDDataAccess):
    def __init__(self, db: SqlAlchemyConnectionFactory):
        super().__init__(User, db, user_rule_validator)   # create() and update() run it

    @ParameterRuleValidator(user_rule_validator, 'data')  # your own method: validate `data` first
    def update_by_email(self, email: str, data: dict) -> int:
        with self._db.get() as session:
            return session.query(User).filter(User.email == email).update(data)
```

### What happens

```python
user_data_access = UserDataAccess(db)
user = user_data_access.create({
    User.email.key: 'jon@example.com',
    User.height.key: '180',              # stored as 180
    User.birthday.key: '1990-04-01',     # stored as 1990-04-01 (parsed by dateutil)
})

user_data_access.update(user.id, {User.height.key: 20})       # PermissionError: the custom validator returned False
user_data_access.update(user.id, {User.height.key: 'tall'})   # PermissionError: expected `int`
user_data_access.update(user.id, {'nickname': 'jj'})          # PermissionError: no rule for `nickname`
user_data_access.update(user.id, {User.height.key: None})     # allowed: the rule is nullable
user_data_access.update_by_email('jon@example.com', {User.agreement.key: True})   # returns 1
```

The `height` validator starts with `height is None or`: a custom validator is also called with `None`, and `None > 50` would raise (which is reported as a `PermissionError` too).

## Built-in converters and validators

`core_lib.rule_validator.helpers` has ready-made functions for `custom_converter` and `custom_validator`:

- `convert_location(location)`: turns `{'lat': ..., 'lng': ...}` or `{'latitude': ..., 'longitude': ...}` into a WKT string `'POINT(lng lat)'`. `None` stays `None`. There are two catches. It needs a dict: a string or a list raises `AttributeError` (see `custom_converter` below). And with the short keys, a coordinate of exactly `0` counts as missing, because the helper uses `or` to fall back from `lat` to `latitude`: `{'lat': 0, 'lng': 34.7818}` becomes `'POINT(34.7818 None)'` and fails `validate_location`. Send points on the equator or the prime meridian with the long keys: `{'latitude': 0, 'longitude': 34.7818}` becomes `'POINT(34.7818 0)'`.
- `validate_location(point)`: takes that WKT string and returns `True` when latitude is within -90..90 and longitude within -180..180. `None` is valid.
- `convert_datetime(value)`: turns an `int`/`float` Unix timestamp or a `date` into a `datetime`. A falsy value (`None`, `0`) becomes `None`; anything else is returned as is.

For example, for a geoalchemy2 `Geometry('POINT')` column:

```python
from sqlalchemy import Column, Integer
from geoalchemy2 import Geometry
from core_lib.data_layers.data.db.sqlalchemy.base import Base
from core_lib.rule_validator.helpers import convert_location, validate_location
from core_lib.rule_validator.rule_validator import RuleValidator, ValueRuleValidator


class Place(Base):
    __tablename__ = 'place'

    id = Column(Integer, primary_key=True)
    location = Column(Geometry('POINT'))


place_rule_validator = RuleValidator([
    ValueRuleValidator(Place.location.key, dict, custom_converter=convert_location, custom_validator=validate_location),
])

place_rule_validator.validate_dict({Place.location.key: {'lat': 32.0853, 'lng': 34.7818}})
# {'location': 'POINT(34.7818 32.0853)'}
place_rule_validator.validate_dict({Place.location.key: {'lat': 132.0, 'lng': 34.7818}})
# PermissionError: validate_location returned False (latitude 132 is out of range)
```

`validate_location` receives the WKT string, not the dict: a custom validator always gets the value after `custom_converter` has run.

## ValueRuleValidator

*core_lib.rule_validator.rule_validator.ValueRuleValidator* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/rule_validator/rule_validator.py#L5){:target="_blank"}

`ValueRuleValidator` defines the rule for one key in the input dict.

```python
class ValueRuleValidator(object):

    def __init__(
        self,
        key: str,
        value_type,
        nullable: bool = True,
        custom_validator=None,
        custom_converter=None
    ):
    ...
```

**Arguments**

- **`key`** *`(str)`*: The key this rule applies to. Use `Entity.column.key`.
- **`value_type`**: The expected Python type, such as `str`, `int`, `bool`, `datetime.date`.
- **`nullable`** *`(bool)`*: Default `True`. When `False`, `None` fails validation.
- **`custom_validator`**: Optional function called with the converted value. It must return exactly `True`; any other return value, or an exception, raises `PermissionError`. When the value is `None` and the rule is nullable, a non-`True` return is ignored, but an exception still raises.
- **`custom_converter`**: Optional function that converts the value. When it is set, `value_type` is not checked, and an exception the converter raises is not wrapped in `PermissionError`. So the converter must handle wrong-typed input itself: with `convert_location`, a client that sends `'32.08,34.78'` instead of a dict gets `AttributeError: 'str' object has no attribute 'get'`, not a `PermissionError`.

**How one value is checked, in order**

1. `None` with `nullable=False` raises.
2. If `custom_converter` is set, the value is converted and the type check is skipped. An exception from the converter propagates as-is.
3. Otherwise, for a truthy value: a `str` rule converts an `int` or `float` to a string; an `int` rule converts a string of digits such as `'180'` (any other string, `'-5'` included, raises); a `datetime.datetime` or `datetime.date` rule parses a string with `dateutil` (and returns a `datetime` even for a `date` rule). Any other value must be an instance of `value_type`.
4. `custom_validator`, if set, runs on the result.

A falsy value (`0`, `''`, `False`, `[]`, `{}`) skips the type check in step 3, so `''` passes an `int` rule. `bool` is a subclass of `int` in Python, so `True` passes an `int` rule too. Use `custom_validator` when you need to reject those.

## RuleValidator

*core_lib.rule_validator.rule_validator.RuleValidator* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/rule_validator/rule_validator.py#L14){:target="_blank"}

`RuleValidator` groups field rules and applies them to an input dict.

### RuleValidator.\_\_init\_\_

*core_lib.rule_validator.rule_validator.RuleValidator.\_\_init\_\_* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/rule_validator/rule_validator.py#L15){:target="_blank"}

```python
class RuleValidator(object):

    def __init__(
        self,
        value_rule_validators: list,
        strict_mode: bool = True,
        strict_output: bool = False,
        mandatory_keys: list = [],
        prohibited_keys: list = [],
    ):
```

**Arguments**

- **`value_rule_validators`** *`(list)`*: The `ValueRuleValidator` rules, one per key.
- **`strict_mode`** *`(bool)`*: Default `True`. Stored as a fallback; see the note below.
- **`strict_output`** *`(bool)`*: Default `False`. Stored as a fallback; see the note below.
- **`mandatory_keys`** *`(list)`*: Keys that must appear in every input dict.
- **`prohibited_keys`** *`(list)`*: Keys that must not appear in any input dict.

> **The constructor's `strict_mode` and `strict_output` are used only when `validate_dict()` receives `None` for them.** `validate_dict()` defaults to `strict_mode=True, strict_output=False`, so `RuleValidator(rules, strict_mode=False).validate_dict(data)` is still strict. Pass the flags to `validate_dict()` when you call it yourself. `@ParameterRuleValidator` passes its own `strict_mode`, which defaults to `None`, so there the constructor's `strict_mode` does apply; it never passes `strict_output`, so the constructor's `strict_output` has no effect there.

### RuleValidator.update()

*core_lib.rule_validator.rule_validator.RuleValidator.update()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/rule_validator/rule_validator.py#L31){:target="_blank"}

Adds or replaces rules at runtime. Each `ValueRuleValidator` replaces any existing rule with the same key. Anything that is not a `ValueRuleValidator` raises `ValueError`.

```python
def update(self, additional_validators):
```

**Arguments**

- **`additional_validators`** *`(list)`*: List of `ValueRuleValidator` instances to add or overwrite.

### RuleValidator.remove()

*core_lib.rule_validator.rule_validator.RuleValidator.remove()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/rule_validator/rule_validator.py#L40){:target="_blank"}

Removes a single rule by its key. Does nothing if the key is not present.

```python
def remove(self, rule_validator_key: str):
```

**Arguments**

- **`rule_validator_key`** *`(str)`*: The key of the `ValueRuleValidator` to remove.

### RuleValidator.validate_dict()

*core_lib.rule_validator.rule_validator.RuleValidator.validate_dict()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/rule_validator/rule_validator.py#L44){:target="_blank"}

Validates the input dict, applies conversions, and returns a new dict. Raises `PermissionError` on the first problem (an exception from a `custom_converter` propagates unchanged).

```python
def validate_dict(
    self,
    update_dict: dict,
    strict_mode: bool = True,
    strict_output: bool = False,
    mandatory_keys: list = None,
    prohibited_keys: list = None,
) -> dict:
```

**Arguments**

- **`update_dict`** *`(dict)`*: Data to validate.
- **`strict_mode`** *`(bool)`*: Default `True`. Pass `None` to use the constructor's value.
- **`strict_output`** *`(bool)`*: Default `False`. Pass `None` to use the constructor's value. Only matters when `strict_mode` is `False`.
- **`mandatory_keys`** *`(list)`*: Replaces the constructor's list for this call. An empty list or `None` uses the constructor's list.
- **`prohibited_keys`** *`(list)`*: Same, for prohibited keys.

What happens to a key that has no rule:

| `strict_mode` | `strict_output` | Key with no rule |
|---|---|---|
| `True` (default) | any | raises `PermissionError` |
| `False` | `False` (default) | kept in the result, unchecked |
| `False` | `True` | dropped from the result |

How Core-Lib itself calls it:

- `CRUD.update(id, data)` calls `validate_dict(data)`: strict, so a key with no rule raises.
- `CRUD.create(data)` calls `validate_dict(data, strict_mode=False)`: a key with no rule is kept, and `create()` then ignores it if the entity has no such attribute.
- `@ParameterRuleValidator` calls `validate_dict(data, strict_mode=<its strict_mode>, mandatory_keys=..., prohibited_keys=...)`.

**Returns**

*`(dict)`*: The validated dict, with converted values.

## ParameterRuleValidator

*core_lib.rule_validator.rule_validator_decorator.ParameterRuleValidator* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/rule_validator/rule_validator_decorator.py#L7){:target="_blank"}

A decorator for your own DataAccess methods. It validates one `dict` argument with a `RuleValidator`, then calls the method with the validated (converted) dict in its place.

```python
class ParameterRuleValidator(object):
    def __init__(
        self,
        rule_validator: RuleValidator,
        parameter_name: str,
        strict_mode: bool = None,
        mandatory_keys: list = None,
        prohibited_keys: list = None,
    ):
```

**Arguments**

- **`rule_validator`** *`(RuleValidator)`*: The rules to apply.
- **`parameter_name`** *`(str)`*: Name of the method parameter that holds the dict, e.g. `'data'`.
- **`strict_mode`** *`(bool)`*: Default `None`, which uses the `RuleValidator` constructor's `strict_mode`.
- **`mandatory_keys`**, **`prohibited_keys`** *`(list)`*: Passed to `validate_dict()`.

**Things to know**

- Pass the dict **positionally**: `update_by_email('jon@example.com', {...})`. Passed as a keyword, `update_by_email('jon@example.com', data={...})`, the decorator raises `IndexError` instead of validating it.
- A value that is not a `dict` raises `ValueError`.
- A caller may pass `additional_validators=[ValueRuleValidator(...)]` as a keyword argument. Those rules are added to the shared `RuleValidator` for this call and removed by key afterwards, and the keyword is still passed on, so the method must accept an `additional_validators` parameter. Because removal is by key, it also deletes a permanent rule with the same key, and if validation fails the extra rules are not removed. A second `RuleValidator` is usually simpler.

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="result_to_dict.html">Previous</a></button>
    <button class="pageNext-btn"><a href="migrations.html">Next</a></button>
</div>
