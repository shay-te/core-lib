---
id: rules_validator
title: Rules Validator
sidebar_label: Rules Validator
---

`RuleValidator` decorator will make sure the `dict` parameter passed to a function is valid accourting to predefined rules.

### Example

##### user_data_access.py

```python
from core_lib.rule_validator.rule_validator import ValueRuleValidator, RuleValidator
from core_lib.rule_validator.rule_validator_decorator import ParameterRuleValidator
from core_lib.helpers.validation import is_int_enum
from your_core_lib.data_layers.data.db.entities.user import User

def enum_gender_converter(value):
  if isinstance(value, str):
    return User.Gender.MALE if (value.lower() == 'male') else User.Gender.FEMALE
  else:
    return User.Gender(value)


def location_convertor(location: dict):
	latitude = location.get('lat') or location.get('latitude')
  longitude = location.get('lng') or location.get('longitude')
  return Point.to_point_str(longitude, latitude)


allowed_update_types = [
  ValueRuleValidator(User.email.key, str),
  ValueRuleValidator(User.password.key, bytes),
  ValueRuleValidator(User.agreement.key, bool),
  ValueRuleValidator(User.location.key, dict, custom_converter=location_convertor, custom_validator=location_validate),
  ValueRuleValidator(User.gender.key, int, custom_converter=lambda value: enum_gender_converter(value), custom_validator=lambda value: is_int_enum(value, User.Gender)),
  ValueRuleValidator(User.height.key, int, custom_validator=lambda value: True if value > 50 else False),
  ValueRuleValidator(User.birthday.key, datetime.date),
]
rule_validator = RuleValidator(allowed_update_types)

class UserDataAccess(DataAccess):

  def __init__(self, db: SqlAlchemyConnectionRegistry):
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



##### user.py

```python
from sqlalchemy import Column, Date, Integer, VARCHAR, BOOLEAN, LargeBinary

from core_lib.data_layers.data.db.sqlalchemy.base import Base
from core_lib.data_layers.data.db.sqlalchemy.types.int_enum import IntEnum

class User(Base):
  __tablename__ = 'user'
  
  class Gender(enum.Enum):
    MALE = 1
    FEMALE = 2
    
  id = Column(Integer, primary_key=True, nullable=False)
	email = Column(VARCHAR(length=255), nullable=False)
  password = Column(LargeBinary(length=255))
  agreement = Column(BOOLEAN(), default=False, nullable=False)
  gender = Column('gender', IntEnum(Gender))
  height = Column(Integer)
	birthday = Column(Date)
```



# RuleValidator

*core_lib.rule_validator.rule_validator.RuleValidator* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/rule_validator/rule_validator.py#L14)

`RuleValidator` class will be configured in the constructor for what rules 

It can be used before creating or updating data from the user.

When `RuleValidator` fails it will raise a `PermissionError` 



### RuleValidator.\_\_init\_\_

*core_lib.rule_validator.rule_validator.RuleValidator.\_\_init\_\_* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/rule_validator/rule_validator.py#L15)

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

- **`value_rule_validators`** *`(list)`*: A list of `ValueRuleValidator` objects that define all fields to validate on the input `dict`.
- **`strict_mode`** *`(bool)`*: Default `True`, When `True` each key in the dictionary must have a rule.
- **`strict_output`** *`(bool)`*: Default `False`, When `True` and `strict_mode` is `True` output `dict` will contain only keys that appear in the rules.
- **`mandatory_keys`** *`(list)`*: List of `keys` that must be inside the validated rules.
- **`prohibited_keys`** *`(list)`*: List of `keys` that can't be inside the dictionary data.

### RuleValidator.validate_dict

*core_lib.rule_validator.rule_validator.RuleValidator.validate_dict()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/rule_validator/rule_validator.py#L37)

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



# ValueRuleValidator

*core_lib.rule_validator.rule_validator.ValueRuleValidator* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/rule_validator/rule_validator.py#L5)


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
- **`value_type`**: The type of the `value` for that `key`.
- **`nullable`** *`(bool)`*: Default `True`, Can the value be `None`.
- **`custom_validator`**: Default `None`, Callback function that return `True`/`False` if the value is valid.
- **`custom_converter`**: Default `None`, Callback function that convert can convert the value and value type.

# Example using ORM

Look at the example here

