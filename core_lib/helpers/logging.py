import logging
from functools import wraps


class Logging(object):
    def __init__(self, message: str = '', level: int = logging.INFO):
        self.message = message
        self.level = level

    def __call__(self, func, *args, **kwargs):
        @wraps(func)
        def __wrapper(*args, **kwargs):
            logging.basicConfig(level=self.level)
            logging.getLogger(func.__qualname__).log(self.level, f'{self.message}')
            return func(*args, **kwargs)

        return __wrapper
