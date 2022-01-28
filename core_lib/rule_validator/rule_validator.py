import datetime
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
                 strict_output: bool = False,
                 mandatory_keys: list = [],
                 prohibited_keys: list = []):
        self.strict_mode = strict_mode
        self.strict_output = strict_output
        self.mandatory_keys = mandatory_keys
        self.prohibited_keys = prohibited_keys

        self.rules = {}
        for rule_validator in value_rule_validators:
            if not isinstance(rule_validator, ValueRuleValidator):
                raise ValueError("RuleValidator.value_rule_validators can only be from type `{}`".format(ValueRuleValidator.__class__.__name__))
            self.rules[rule_validator.key] = rule_validator

    def validate_dict(self,
                      update_dict: dict,
                      strict_mode: bool = True,
                      strict_output: bool = False,
                      mandatory_keys: list = None,
                      prohibited_keys: list = None):

        is_strict_mode = strict_mode if strict_mode is not None else self.strict_mode
        is_strict_output = strict_output if strict_output is not None else self.strict_output

        for mandatory_key in (mandatory_keys or self.mandatory_keys):
            if mandatory_key not in update_dict:
                raise PermissionError("mandatory_key: `{}`. is missing in update_value.".format(mandatory_key))

        result_dict = {}
        for key, value in update_dict.items():

            if key in (prohibited_keys or self.prohibited_keys):
                raise PermissionError("key:`{}`. is listed under `RuleValidator.prohibited_keys`".format(key))

            if key in self.rules:
                result_dict[key] = self._validate_rule(self.rules[key], key, value)
            else:
                if is_strict_mode:
                    raise PermissionError("no `ValueRuleValidator` found for key: `{}`".format(key))
                if not is_strict_output:
                    result_dict[key] = value

        return result_dict

    def _validate_rule(self, rule, key, value):
        parsed_value = value

        if not rule.nullable and value is None:
            raise PermissionError("Can't update key:`{}` column value cannot be null (`ValueRuleValidator.nullable` is set to `True`)".format(key))

        if rule.custom_converter:
            parsed_value = rule.custom_converter(value)

        # `number` to `str`
        elif value and rule.value_type is str and type(value) in [int, float]:
            parsed_value = str(value)

        # `str` to `int`
        elif value and rule.value_type is int and type(value) is str:
            if value.isdigit():
                parsed_value = int(value)
            else:
                raise PermissionError(f"Invalid update key:`{key}` expected `int`, got `{type(value)}`")
        # `str` to `datetime`
        elif value and rule.value_type in [datetime.datetime, datetime.date] and type(value) is str:
            try:
                parsed_value = datetime_parser.parse(value)
            except BaseException as ex:
                raise PermissionError("Invalid update key:`{}` illegal datetime formatted value `{}`. only ISO format is accepted".format(key, value)) from ex

        elif value and rule.value_type is not type(parsed_value):
            raise PermissionError("Invalid update key:`{}` illegal type `{}`".format(key, type(parsed_value)))

        try:
            if rule.custom_validator and rule.custom_validator(parsed_value) is not True:
                raise PermissionError("Update of key:`{}` failed by custom validation".format(key))
        except BaseException as ex:
            raise PermissionError("Error running custom validator with  `{}` and value `{}`".format(key, parsed_value)) from ex

        return parsed_value

