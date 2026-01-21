import datetime
import dateutil.parser as datetime_parser


class ValueRuleValidator(object):
    def __init__(self, key: str, value_type, nullable: bool = True, custom_validator=None, custom_converter=None):
        self.key = key
        self.value_type = value_type
        self.nullable = nullable
        self.custom_validator = custom_validator
        self.custom_converter = custom_converter


class RuleValidator(object):
    def __init__(
        self,
        value_rule_validators: list,
        strict_mode: bool = True,
        strict_output: bool = False,
        mandatory_keys: list = [],
        prohibited_keys: list = [],
    ):
        self.strict_mode = strict_mode
        self.strict_output = strict_output
        self.mandatory_keys = mandatory_keys
        self.prohibited_keys = prohibited_keys

        self.rules = {}
        self.update(value_rule_validators)

    def update(self, additional_validators):
        for rule_validator in additional_validators:
            if not isinstance(rule_validator, ValueRuleValidator):
                raise ValueError(
                    f'RuleValidator.value_rule_validators can only be from type '
                    f'{ValueRuleValidator.__class__.__name__}'
                )
            self.rules[rule_validator.key] = rule_validator

    def remove(self, rule_validator_key: str):
        if rule_validator_key in self.rules:
            del self.rules[rule_validator_key]

    def validate_dict(
        self,
        update_dict: dict,
        strict_mode: bool = True,
        strict_output: bool = False,
        mandatory_keys: list = None,
        prohibited_keys: list = None,
    ) -> dict:

        is_strict_mode = strict_mode if strict_mode is not None else self.strict_mode
        is_strict_output = strict_output if strict_output is not None else self.strict_output

        for mandatory_key in mandatory_keys or self.mandatory_keys:
            if mandatory_key not in update_dict:
                raise PermissionError(f'mandatory_key: `{mandatory_key}`. is missing in update_value.')

        result_dict = {}
        for key, value in update_dict.items():

            if key in (prohibited_keys or self.prohibited_keys):
                raise PermissionError(f'key:`{key}`. is listed under `RuleValidator.prohibited_keys`')

            if key in self.rules:
                result_dict[key] = self._validate_rule(self.rules[key], key, value)
            else:
                if is_strict_mode:
                    raise PermissionError(f'no `ValueRuleValidator` found for key: `{key}`')
                if not is_strict_output:
                    result_dict[key] = value

        return result_dict

    def _validate_rule(self, rule, key, value):
        parsed_value = value

        if not rule.nullable and value is None:
            raise PermissionError(
                f'Can\'t update key:{key} column value cannot be null '
                f'(`ValueRuleValidator.nullable` is set to `True`)'
            )

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
                raise PermissionError(f'Invalid update key:`{key}` expected `int`, got `{type(value)}`')
        # `str` to `datetime`
        elif value and rule.value_type in [datetime.datetime, datetime.date, datetime.time] and type(value) is str:
            try:
                parsed_value = datetime_parser.parse(value)
            except BaseException as ex:
                raise PermissionError(
                    f'Invalid update key:{key} illegal datetime formatted value {value}. '
                    f'only ISO format is accepted'
                ) from ex

        elif value and not isinstance(parsed_value, rule.value_type):
            raise PermissionError(f'Invalid update key:`{key}` illegal type `{type(parsed_value)}` expected {rule.value_type}')

        try:
            if rule.custom_validator:
                custom_valid = rule.custom_validator(parsed_value)
                is_allow_null = parsed_value == None and rule.nullable
                if custom_valid is not True and not is_allow_null:
                    raise PermissionError(f'Update of key:`{key}` failed by custom validation')
        except BaseException as ex:
            raise PermissionError(f'Error running custom validator with  `{key}` and value `{parsed_value}`') from ex

        return parsed_value
