---
id: rules_validator
title: Rules Validator
sidebar: core_lib_doc_sidebar
permalink: rules_validator.html
folder: core_lib_doc
toc: false
---

`RuleValidator` decorator will make sure the `dict` parameter passed to a function is valid accourting to predefined rules. When validation fails a `PermissionError` will be raised

### Example

### `user_data_access.py`

```python
from core_lib.rule_validator.rule_validator import ValueRuleValidator, RuleValidator
from core_lib.rule_validator.rule_validator_decorator import ParameterRuleValidator
from core_lib.helpers.validation import is_int_enum
from core_lib.data_layers.data.db.sqlalchemy.types.point import Point
from your_core_lib.data_layers.data.db.entities.user import User

def location_convertor(location: dict):
	latitude = location.get('lat') or location.get('latitude')
  longitude = location.get('lng') or location.get('longitude')
  return Point.to_point_str(longitude, latitude)


allowed_update_types = [
  ValueRuleValidator(User.email.key, str),
  ValueRuleValidator(User.password.key, bytes),
  ValueRuleValidator(User.agreement.key, bool),
  ValueRuleValidator(User.location.key, dict, custom_converter=location_convertor, custom_validator=location_validate),
  ValueRuleValidator(User.height.key, int, custom_validator=lambda value: True if value > 50 else False),
  ValueRuleValidator(User.birthday.key, datetime.date),
]
rule_validator = RuleValidator(allowed_update_types)

class UserDataAccess(DataAccess):

  def __init__(self, db: SqlAlchemyConnectionFactory):
    self.logger = logging.getLogger(self.__class__.__name__)
    self._db = db

  @ParameterRuleValidator(rule_validator, 'data', strict_mode=False)
  def create(self, data: dict) -> User:
    with self._db.get() as session:
      user = User()
      for key, value in data.items():
        if key != 'id' and hasattr(u	ser, key):
            setattr(user, key, value)
      session.add(user)
    return user

  @ParameterRuleValidator(rule_validator, 'data')
  def update(self, user_id: int, data):
    with self._db.get() as session:
      session.query(User).filter(User.id == user_id).update(data)
```



### `user.py`

```python
from sqlalchemy import Column, Date, Integer, VARCHAR, BOOLEAN, LargeBinary
from geoalchemy2.types import Geometry

from core_lib.data_layers.data.db.sqlalchemy.base import Base

class User(Base):
  __tablename__ = 'user'
    
  id = Column(Integer, primary_key=True, nullable=False)
	email = Column(VARCHAR(length=255), nullable=False)
  password = Column(LargeBinary(length=255))
  agreement = Column(BOOLEAN(), default=False, nullable=False)
  height = Column(Integer)
	birthday = Column(Date)
  location = Column(Geometry('POINT'))
```



# ValueRuleValidator

*core_lib.rule_validator.rule_validator.ValueRuleValidator* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/rule_validator/rule_validator.py#L5){:target="_blank"}

`ValueRuleValidator` defines the validation rule for a specific field in the validated `dict` object


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

- **`key`** *`(str)`*: The key in the `dict`, that this rule is apply for.
- **`value_type`**: The type of value associated with the specified `key`.
- **`nullable`** *`(bool)`*: Default `True`, When `nullable` is set to `False,` and the value associated with the `key` is  `None`, The validation will fail
- **`custom_validator`**: Default `None`, Custom `Callback` function that returns `True`/`False` if the value is valid or not.
- **`custom_converter`**: Default `None`, Custom `Callback` function that converts the value associated with the key to any value and type.



# RuleValidator

*core_lib.rule_validator.rule_validator.RuleValidator* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/rule_validator/rule_validator.py#L14){:target="_blank"}

`RuleValidator` class will be configured in the constructor with the following parameters 

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

- **`value_rule_validators`** *`(list)`*: A list of `ValueRuleValidator` objects that define all fields to validate on the input `dict` object.
- **`strict_mode`** *`(bool)`*: Default `True`, When `True` each key in the dictionary must have a rule.
- **`strict_output`** *`(bool)`*: Default `False`, When `True` and `strict_mode` is `True` output `dict` will contain only keys that appear in the rules.
- **`mandatory_keys`** *`(list)`*: List of `keys` that must be inside the validated rules.
- **`prohibited_keys`** *`(list)`*: List of `keys` that can't be inside the dictionary data.



### RuleValidator.validate_dict

*core_lib.rule_validator.rule_validator.RuleValidator.validate_dict()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/rule_validator/rule_validator.py#L37){:target="_blank"}

`validate_dict` function will perform the `dict` validation and conversion 

```python
class RuleValidator(object):

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

- **`update_dict`** *`(dict)`*: A `dict` of data we need to validate.
- **`strict_mode`** *`(bool)`*: Override the default `self.strict_mode` for this specific validation.
- **`strict_output`** *`(bool)`*: Override the default `self.strict_output` for this specific validation.
- **`mandatory_keys`** *`(list)`*: Override the default `self.mandatory_keys` for this specific validation.
- **`prohibited_keys`** *`(list)`*: Override the default `self.prohibited_keys` for this specific validation.

**Returns**

*`(dict)`*: Validated dict.



# Nested validation

`ValueRuleValidator` has no built-in nested option, but a `custom_validator` can run another `RuleValidator` over a nested `dict` or over every `dict` in a `list`.

```python
from core_lib.rule_validator.rule_validator import ValueRuleValidator, RuleValidator

item_rule_validator = RuleValidator(
    [ValueRuleValidator('name', str, nullable=False), ValueRuleValidator('size', int)],
    mandatory_keys=['name'],
)

rule_validator = RuleValidator([
    # a list of dicts: every item must pass `item_rule_validator`
    ValueRuleValidator(
        'items', list, nullable=False,
        custom_validator=lambda items: isinstance(items, list) and all(
            isinstance(item, dict) and item_rule_validator.validate_dict(item) is not None for item in items),
    ),
    # a nested dict
    ValueRuleValidator(
        'settings', dict,
        custom_validator=lambda settings: item_rule_validator.validate_dict(settings) is not None,
    ),
])

rule_validator.validate_dict({'items': [{'name': 'widget', 'size': 2}], 'settings': {'name': 'acme'}})  # passes
rule_validator.validate_dict({'items': [{'name': 'widget', 'unknown': 1}]})  # raises PermissionError
```

### Hierarchical (multi-level) validation

Nesting is not limited to one level: a nested `RuleValidator` can itself hold rules whose `custom_validator` runs the next `RuleValidator` down, so you can validate a whole tree. Build it **bottom-up**: define the innermost validator first, then each parent's rule calls the validator of the level below. Two small helpers keep every level readable:

```python
from core_lib.rule_validator.rule_validator import ValueRuleValidator, RuleValidator


def dict_of(inner: RuleValidator):
    # value must be a dict that passes `inner`
    return lambda value: isinstance(value, dict) and inner.validate_dict(value) is not None


def list_of(inner: RuleValidator):
    # value must be a list whose every item is a dict that passes `inner`
    return lambda value: isinstance(value, list) and all(
        isinstance(item, dict) and inner.validate_dict(item) is not None for item in value)


# level 4 (innermost): a product's options
option_rule_validator = RuleValidator([
    ValueRuleValidator('color', str),
    ValueRuleValidator('size', int),
])

# level 3: a product, with a nested options dict
product_rule_validator = RuleValidator([
    ValueRuleValidator('name', str, nullable=False),
    ValueRuleValidator('options', dict, custom_validator=dict_of(option_rule_validator)),
], mandatory_keys=['name'])

# level 2: a category, with a list of products
category_rule_validator = RuleValidator([
    ValueRuleValidator('name', str, nullable=False),
    ValueRuleValidator('products', list, nullable=False, custom_validator=list_of(product_rule_validator)),
], mandatory_keys=['name', 'products'])

# level 1 (root): the catalog, with a list of categories
catalog_rule_validator = RuleValidator([
    ValueRuleValidator('categories', list, nullable=False, custom_validator=list_of(category_rule_validator)),
], mandatory_keys=['categories'])


catalog = {
    'categories': [
        {'name': 'tools', 'products': [
            {'name': 'widget', 'options': {'color': 'red', 'size': 2}},
            {'name': 'gadget'},
        ]},
        {'name': 'empty', 'products': []},
    ],
}
catalog_rule_validator.validate_dict(catalog)  # passes, returns `catalog` unchanged

bad_catalog = {'categories': [{'name': 'tools', 'products': [{'name': 'widget', 'options': {'weight': 1}}]}]}
try:
    catalog_rule_validator.validate_dict(bad_catalog)  # `weight` has no rule four levels down
except PermissionError as error:
    cause = error
    while cause is not None:  # walk from the root rule down to the rejected key
        print(cause)
        cause = cause.__cause__
```

The printed chain has one line per level, from the root down to the real reason (values shortened here):

```
Error running custom validator with  `categories` and value `[...]`
Error running custom validator with  `products` and value `[...]`
Error running custom validator with  `options` and value `{'weight': 1}`
no `ValueRuleValidator` found for key: `weight`
```

Every level applies its own rules independently, so `mandatory_keys`, `nullable`, `strict_mode` (unknown keys) and type checks work at each depth: a category missing `products`, a product with `name: None`, or an unknown key in `options` are all rejected.

**How it behaves**

- **A nested failure fails the whole `dict`.** Any exception raised inside a `custom_validator`, including the inner `PermissionError`, is re-raised as a `PermissionError` for the outer key, with the inner exception as its `__cause__`. The top-level message is generic (`Error running custom validator with <key> ...`). The specific reason, such as a missing mandatory key or a key with no rule, is at the end of the cause chain, so log the full traceback.
- **Return exactly `True`.** A `custom_validator` result that is not `True` fails validation, so return a `bool`. `validate_dict(...) is not None` does that for a nested call.
- **Check the type yourself for falsy values.** `RuleValidator` skips its own type check when the value is falsy, so `{}` would pass a `list` rule. Keep the `isinstance(...)` inside the `custom_validator`.
- **Inner conversions are not applied.** The nested `validate_dict` result is only checked, never written back, so the output keeps the original nested values (e.g. `'2'` stays `'2'` even when the inner rule is `int`).
- **Depth.** Each level is one more `custom_validator` call. Four levels are covered by the tests, and 200 levels have been measured to work. Past Python's recursion limit (around 300 levels with the default limit of 1000), the `RecursionError` is caught like any other exception and reported as a `PermissionError`, so valid data is rejected with a misleading message. Keep nesting shallow.

Covered by `tests/test_db_rule_validator.py` (`test_2` to `test_6`).

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/result_to_dict.html"><< Previous</a></button>
    <button class="pageNext-btn"><a href="/migrations.html">Next >></a></button>
</div>