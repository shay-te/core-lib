import inspect
import logging
from string import Formatter

logger = logging.getLogger(__name__)


class UnseenFormatter(Formatter):

    def get_value(self, key, args, kwargs):
        try:
            if isinstance(key, int) and key < len(args):
                return args[key]
            if isinstance(key, str) and key in kwargs:
                return kwargs[key]
            return '!M!'
        except BaseException as ex:
            logger.warning('Error while building key. `{}`'.format(key), exc_info=True)
            return '!E!'


class CacheKeyGenerator(object):

    _formatter = UnseenFormatter()

    def __init__(self, max_key_length: int):
        self.max_key_length = max_key_length

    def generate_key(self, key: str, func, *args, **kwargs):
        if key:
            params = [k[0] for k in inspect.signature(func).parameters.items()]
            format_params = {**{p: p for p in params}, **kwargs}

            for index, arg in enumerate(args):
                if params[index] != 'self':
                    param_name = params[index]
                    format_params[param_name] = args[index]

            new_key = CacheKeyGenerator._formatter.format(key, **format_params)
        else:
            new_key = func.__qualname__

        return new_key[:self.max_key_length]
