import inspect
import logging
from contextlib import suppress
from functools import wraps

from core_lib.helpers.func_utils import build_value_by_func_parameters


class Logging(object):

    def __init__(self, message: str = '', level: int = logging.INFO, stack_depth=1):
        self.message = message
        self.level = level
        self.calling_module = None

        stack = inspect.stack()
        frame = stack[stack_depth]

        with suppress(Exception):
            self.calling_module = frame[0].f_globals[frame[3]].__module__
        if not self.calling_module:
            with suppress(Exception):
                self.calling_module = frame[0].f_locals["self"].__module__
        if not self.calling_module:
            with suppress(Exception):
                self.calling_module = frame[0].f_locals['__module__']
        if not self.calling_module:
            self.calling_module = __name__

    def __call__(self, func, *args, **kwargs):

        @wraps(func)
        def __wrapper(*args, **kwargs):
            message = build_value_by_func_parameters(self.message, func, *args, **kwargs)
            logging.getLogger(self.calling_module).log(self.level, '{}. {}'.format(self.message, ', '.join(message)))
            return func(*args, **kwargs)

        return __wrapper



