import logging
from functools import wraps

from core_lib.helpers.func_utils import build_value_by_func_parameters


class Logging(object):
    def __init__(self, message: str = '', level: int = logging.INFO):
        self.message = message
        self.level = level

    def __call__(self, func, *args, **kwargs):
        @wraps(func)
        def __wrapper(*args, **kwargs):
            formatted_message = build_value_by_func_parameters(self.message, func, *args, **kwargs)
            logging.getLogger(func.__qualname__).log(
                self.level, f'{self.message if formatted_message == func.__qualname__ else formatted_message}'
            )
            return func(*args, **kwargs)

        return __wrapper
