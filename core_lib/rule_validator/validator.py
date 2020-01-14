import datetime
import inspect

import dateutil.parser as datetime_parser

from core_lib.data_layers.data.db.base import Base


class RuleValidator(object):

    def __init__(self, type, nullable: bool = True, custom_validator=None, custom_converter=None):
        self.type = type
        self.nullable = nullable
        self.custom_validator = custom_validator
        self.custom_converter = custom_converter


def _validate_dict_by_rules(rules: dict, update_dict: dict):
    for key, value in update_dict.items():
        if key not in rules:
            raise PermissionError('attempt to perform invalid update update key:[{}] is not defined in rules'.format(key))

        rule = rules[key]
        if not isinstance(rule, RuleValidator): raise ValueError('rules must contain RuleValidator class'.format(key))

        if not rule.nullable and value is None:
            raise PermissionError('attempt to perform invalid update update key:[{}] value cannot be null'.format(key))

        parsed_value = value
        if rule.type is int and type(value) is str:
            if value.isdigit():
                parsed_value = int(value)
            else:
                raise PermissionError('attempt to perform invalid update update key:[{}] illegal type [{}]'.format(key, type(value)))
        elif rule.type is datetime.datetime and type(value) is str:
            try:
                parsed_value = datetime_parser.parse(value)
            except Exception:
                raise PermissionError('attempt to perform invalid update update key:[{}] illegal datetime formatted value [{}]. only ISO format is accepted'.format(key, value))
        elif rule.type is not type(value):
            raise PermissionError('attempt to perform invalid update update key:[{}] illegal type [{}]'.format(key, type(value)))

        if rule.custom_validator and rule.custom_validator(parsed_value) is not True:
            raise PermissionError('attempt to perform invalid update update key:[{}] custom validation failed'.format(key))


def _fill_rules_from_orm_entity(rules: dict, base: Base):
    if base:
        mapper = inspect(base).mapper
        for c in mapper.column_attrs:
            print('_fill_rules_from_orm_entity key: {}'.format(c.key))


class ValidationDictParameterByRules(object):

    def __init__(self, rules: int, parameter_name: str, base: Base = None):
        if not rules: raise ValueError('db update validation: rules missing');
        if not isinstance(rules, dict): raise ValueError('db update validation: rules must be of type dict')
        if not parameter_name: raise ValueError('db update validation: parameter_index missing');

        self.rules = rules
        self.parameter_name = parameter_name
        self.base = base

    def __call__(self, func):
        def __wrapper(*args, **kwargs):
            parameters = inspect.signature(func).parameters
            if self.parameter_name not in parameters:
                raise ValueError('dict validation failed on. parameter named: {}. dose not exists in the target function. {} '.format(self.parameter_name, func.__name__))

            parameter_index = list(parameters).index(self.parameter_name)
            update_dict = args[parameter_index]
            if not isinstance(update_dict, dict): raise ValueError('dict validation failed on {}: parameter name: {} must to point to a dict variable'.format(func.__name__, self.parameter_name))

            _fill_rules_from_orm_entity(self.rules, self.base)
            _validate_dict_by_rules(self.rules, update_dict)

            return func(*args, **kwargs)

        return __wrapper
