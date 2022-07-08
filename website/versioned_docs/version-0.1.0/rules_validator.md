---
id: rules_validator
title: Rules Validator
sidebar_label: Rules Validator
---
# RuleValidator

*core_lib.rule_validator.rule_validator.RuleValidator* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/rule_validator/rule_validator.py#L14)

`RuleValidator` on `dict` objects, and offer two responsibilities
1. Validate `dict` structure 
2. Transform `dict` values
     
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

- **`value_rule_validators`** *`(list)`*: A list of `ValueRuleValidator` objects.
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

