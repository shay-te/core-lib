import inspect
import logging
from string import Formatter

logger = logging.getLogger(__name__)


class UnseenFormatter(Formatter):

    def get_value(self, key, args, kwds):
        try:
            if isinstance(key, str):
                return kwds[key]
            else:
                return Formatter.get_value(key, args, kwds)
        except BaseException as ex:
            logger.warning('Error while building key. `{}`'.format(key), exc_info=True)
            return 'E'


class CacheKeyGenerator(object):

    _formatter = UnseenFormatter()

    def __init__(self, max_key_length: int):
        self.max_key_length = max_key_length

    def generate_key(self, key: str, func, *args, **kwargs):
        if key:
            format_params = {}
            args_len = len(args)
            for index, arg in enumerate(inspect.getfullargspec(func).args):
                if arg is not 'self':
                    if index < args_len:
                        format_params[arg] = args[index]
                    else:
                        format_params[arg] = kwargs[arg] if arg in kwargs else '_'  # Handle optional parameters

            new_key = CacheKeyGenerator._formatter.format(key, **format_params)
        else:
            new_key = func.__qualname__

        return new_key[:self.max_key_length]

