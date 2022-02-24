import logging
from functools import wraps

from core_lib.helpers.func_utils import (
    build_value_by_func_parameters,
    generate_key_by_func_parameters,
)


class Logging(object):
    def __init__(self, message: str = '', level: int = logging.INFO, stack_depth=1, log_parameters: bool = False):
        self.message = message
        self.level = level
        self.log_parameters = log_parameters

    def __call__(self, func, *args, **kwargs):
        @wraps(func)
        def __wrapper(*args, **kwargs):
            formatted_params = ""
            if self.log_parameters:
                formatted_params = build_value_by_func_parameters(
                    generate_key_by_func_parameters(func, *args, **kwargs), func, *args, **kwargs
                )

            logging.basicConfig(level=self.level)
            logging.getLogger(func.__qualname__).log(
                self.level, f'{self.message}.{formatted_params}'
            )
            return func(*args, **kwargs)

        return __wrapper
