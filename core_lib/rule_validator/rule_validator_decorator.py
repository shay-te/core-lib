from functools import wraps

from core_lib.helpers.func_utils import get_func_parameter_index_by_name
from core_lib.rule_validator.rule_validator import RuleValidator


class ParameterRuleValidator(object):

    def __init__(self,
                 rule_validator: RuleValidator,
                 parameter_name: str,
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

        @wraps(func)
        def __wrapper(*args, **kwargs):

            parameter_index = get_func_parameter_index_by_name(func, self.parameter_name)
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
