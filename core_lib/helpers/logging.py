import inspect
import logging
from contextlib import suppress
from functools import wraps


class Logging(object):

    def __init__(self, message: str = '', parameters: list = [], level: int = logging.INFO, stack_depth=1):
        self.message = message
        self.parameters = parameters
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
            additional_params = []
            parameters = list(inspect.signature(func).parameters)
            for param in self.parameters:
                parameter_index = parameters.index(param)
                if 0 <= parameter_index < len(args):
                    additional_params.append('{}={}'.format(param, args[parameter_index]))
                else:
                    if param in kwargs:
                        additional_params.append('{}={}'.format(param, kwargs[param]))
                    else:
                        additional_params.append('{}=?'.format(param))

            logging.getLogger(self.calling_module).log(self.level, '{}. {}'.format(self.message, ', '.join(additional_params)))
            return func(*args, **kwargs)

        return __wrapper



