import logging
from functools import wraps

from core_lib.helpers.func_utils import build_value_by_func_parameters, get_calling_module


class Logging(object):

    def __init__(self, message: str = '', level: int = logging.INFO, stack_depth=1):
        self.message = message
        self.level = level
        self.calling_module = get_calling_module(stack_depth)

    def __call__(self, func, *args, **kwargs):
        @wraps(func)
        def __wrapper(*args, **kwargs):
            message = build_value_by_func_parameters(self.message, func, *args, **kwargs)
            logging.getLogger(self.calling_module).log(self.level, '{}.{}'.format(self.message, ''.join(message)))
            return func(*args, **kwargs)

        return __wrapper
