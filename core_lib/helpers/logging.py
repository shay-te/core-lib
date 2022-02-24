import logging
from functools import wraps

from core_lib.helpers.func_utils import build_value_by_func_parameters, get_calling_module, get_func_parameters_as_dict


class Logging(object):

    def __init__(self, message: str = '', log_parameters: bool = False, level: int = logging.INFO, stack_depth=1):
        self.message = message
        self.level = level
        self.calling_module = get_calling_module(stack_depth)
        self.log_parameters = log_parameters

    def __call__(self, func, *args, **kwargs):
        @wraps(func)
        def __wrapper(*args, **kwargs):
            if self.log_parameters:
                params_list = []
                params = get_func_parameters_as_dict(func, *args, **kwargs)
                if params['self']:
                    del(params['self'])
                for key in params:
                    params_list.append("{"+str(key)+"}")
                key_string = "_".join(params_list)
                message = build_value_by_func_parameters(key_string, func, *args, **kwargs)
            else:
                message = ""
            logging.basicConfig(level=self.level)
            logging.getLogger(func.__qualname__).log(self.level, '{}.{}'.format(self.message, ''.join(message)))
            return func(*args, **kwargs)

        return __wrapper
