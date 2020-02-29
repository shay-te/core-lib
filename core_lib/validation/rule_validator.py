import datetime
import inspect

import dateutil.parser as datetime_parser


class ValueRuleValidator(object):

    def __init__(self,
                 key: str,
                 value_type,
                 nullable: bool = True,
                 custom_validator=None,
                 custom_converter=None):
        self.key = key
        self.value_type = value_type
        self.nullable = nullable
        self.custom_validator = custom_validator
        self.custom_converter = custom_converter


class RuleValidator(object):

    def __init__(self,
                 value_rule_validators: list,
                 strict_mode: bool = True,
                 mandatory_keys: list = [],
                 prohibited_keys: list = []):
        self.rules = {}
        self.strict_mode = strict_mode
        self.mandatory_keys = mandatory_keys
        self.prohibited_keys = prohibited_keys

        for rule_validator in value_rule_validators:
            if not isinstance(rule_validator, ValueRuleValidator):
                raise ValueError("RuleValidator.value_rule_validators can only be from type `{}`".format(ValueRuleValidator.__class__.__name__))
            self.rules[rule_validator.key] = rule_validator

    def validate_dict(self,
                      update_dict: dict,
                      strict_mode: bool = None,
                      mandatory_keys: list = None,
                      prohibited_keys: list = None):

        for mandatory_key in (mandatory_keys or self.mandatory_keys):
            if mandatory_key not in update_dict:
                raise PermissionError("mandatory_key: `{}`. is missing in update_value.".format(mandatory_key))

        result_dict = {}
        for key, value in update_dict.items():

            if key in (prohibited_keys or self.prohibited_keys):
                raise PermissionError("key:`{}`. is listed under `RuleValidator.prohibited_keys`".format(key))

            if strict_mode if strict_mode is not None else self.strict_mode:
                if key not in self.rules:
                    raise PermissionError("no `ValueRuleValidator` found for key: `{}`".format(key))
            else:
                if key not in self.rules:
                    continue

            rule = self.rules[key]

            if not rule.nullable and value is None:
                raise PermissionError("Can't update key:`{}` column value cannot be null (`ValueRuleValidator.nullable` is set to `True`)".format(key))

            parsed_value = value

            if rule.custom_converter:
                parsed_value = rule.custom_converter(value)

            # `str` to `int`
            elif rule.value_type is int and type(value) is str:
                if value.isdigit():
                    parsed_value = int(value)
                else:
                    raise PermissionError("Invalid update key:`{}` illegal type `{}`".format(key, type(value)))
            # `str` to `datetime`
            elif rule.value_type is datetime.datetime and type(value) is str:
                try:
                    parsed_value = datetime_parser.parse(value)
                except BaseException as ex:
                    raise PermissionError("Invalid update key:`{}` illegal datetime formatted value `{}`. only ISO format is accepted".format(key, value)) from ex

            elif rule.value_type is not type(parsed_value):
                raise PermissionError("Invalid update key:`{}` illegal type `{}`".format(key, type(parsed_value)))

            if rule.custom_validator and rule.custom_validator(parsed_value) is not True:
                raise PermissionError("Update of key:`{}` failed by custom validation".format(key))

            result_dict[key] = parsed_value

        return result_dict

class ParameterRuleValidator(object):

    def __init__(self,
                 parameter_name: str,
                 rule_validator: RuleValidator,
                 strict_mode: bool = None,
                 mandatory_keys: list = None,
                 prohibited_keys: list = None):

        if not parameter_name:
            raise ValueError("ParameterRuleValidator: parameter_name missing")

        if not rule_validator:
            raise ValueError("ParameterRuleValidator: rule_validator missing")

        self.parameter_name = parameter_name
        self.rule_validator = rule_validator
        self.strict_mode = strict_mode
        self.mandatory_keys = mandatory_keys
        self.prohibited_keys = prohibited_keys

    def __call__(self, func):
        def __wrapper(*args, **kwargs):
            parameters = inspect.signature(func).parameters
            if self.parameter_name not in parameters:
                raise ValueError("`ParameterRuleValidator`. parameter named: {}. dose not exists in the decoratoed function. {} ".format(self.parameter_name, func.__name__))

            parameter_index = list(parameters).index(self.parameter_name)
            update_dict = args[parameter_index]
            if not isinstance(update_dict, dict):
                raise ValueError("`ParameterRuleValidator`. function `{}`, parameter `{}`. apply only when updating the database with `dict` parameters ".format(func.__name__, self.parameter_name))

            updated_dict = self.rule_validator.validate_dict(update_dict,
                                                             strict_mode=self.strict_mode,
                                                             mandatory_keys=self.mandatory_keys,
                                                             prohibited_keys=self.prohibited_keys)

            new_args = list(args)
            new_args[parameter_index] = updated_dict

            return func(*tuple(new_args), **kwargs)

        return __wrapper
