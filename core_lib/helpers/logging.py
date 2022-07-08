import logging
from functools import wraps

from core_lib.helpers.func_utils import build_function_key


class Logging(object):
    def __init__(self, message: str = '', level: int = logging.INFO):
        self.message = message
        self.level = level

    def __call__(self, func, *args, **kwargs):
        @wraps(func)
        def __wrapper(*args, **kwargs):
            formatted_message = build_function_key(self.message, func, *args, **kwargs) if self.message else ''
            logging.getLogger(func.__qualname__).log(self.level, f'{formatted_message}')
            return func(*args, **kwargs)

        return __wrapper
