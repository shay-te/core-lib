---
id: rules_validator
title: Rules Validator
sidebar_label: Rules Validator
---

`RulesValidator` on `dict` objects, and offer two responsibilities
1. validate dict structure 
2. transform dict values
     
it can be used before creating or updating data from the user.

When `RulesValidator` fails it will raise a `PermissionError` 

```python
class RuleValidator(object):

    def __init__(self,
                 value_rule_validators: list,
                 strict_mode: bool = True,
                 strict_output: bool = False,
                 mandatory_keys: list = [], 
                 prohibited_keys: list = []):

        ...
 
    def validate_dict(self,
                               update_dict: dict,
                               strict_mode: bool = True,
                               strict_output: bool = False,
                               mandatory_keys: list = [],
                               prohibited_keys: list = []):
        ...
```

### RuleValidator.\_\_init\_\_
`value_rule_validators` a list of `ValueRuleValidator` objects. 

`strict_mode` when `True`. each key in the `dict` must have a rule  (type: `bool`, default: `True`)

`strict_output` when `True` and `strict_mode` is `True`. output `dict` will contain only keys that appear in the rules (type: `bool`, default: `False`)
  
`mandatory_keys` list of `keys` that must be inside the validated rules. (type: `list`, default: `[]`)
 
`prohibited_keys` list of `keys` that can't be inside the `dict` data. (type: `list`, default: `[]`)

### RuleValidator.validate_dict

`update_dict` a `dict` of data we need to validate (type: `dict`)

`strict_mode` override the default `self.strict_mode` for this specific validation

`strict_output` override the default `self.strict_output` for this specific validation
  
`mandatory_keys` override the default `self.mandatory_keys` for this specific validation
 
`prohibited_keys` override the default `self.prohibited_keys` for this specific validation


# ValueRuleValidator
`key` the key in the `dict`, that this rule is apply for. (type: `str`, mandatory: `True`)
 
`value_type` the type of the `value` for that `key`. ( mandatory: `True`)

`nullable` can the value be `None`.(type: `bool`, default: `True`)

`custom_validator` callback function that return `True`/`False` if the value is valid. (type: `function`, default: `None`)

`custom_converter` callback function that convert can convert the value and value type. (type: `function`, default: `None`)
```python
class ValueRuleValidator(object):

    def __init__(self,
                 key: str, 
                 value_type,
                 nullable: bool = True,
                 custom_validator=None,
                 custom_converter=None):

        ...
```

# Example using ORM

Look at the example here

