
import inspect
from abc import abstractmethod
from datetime import timedelta


class CacheBase(object):

    def __init__(self, key: str = None, expire: timedelta = None, invalidate: bool = False):
        self.key = key
        self.expire = expire
        self.invalidate = invalidate

    def __call__(self, func, *args, **kwargs):

        def __wrapper(*args, **kwargs):
            key = self.__generate_key(func, *args, **kwargs)
            if self.invalidate:
                self.invalidate_cache(key)
                return func(*args, **kwargs)
            else:
                result = self.from_cache(key)
                if not result:
                    result = func(*args, **kwargs)
                    self.to_cache(key, result, self.expire)
                return result

        return __wrapper

    def __generate_key(self, func, *args, **kwargs):
        if self.key:
            format_params = {}
            for index, arg in enumerate(inspect.getfullargspec(func).args):
                if arg is not 'self':
                    format_params[arg] = args[index]
            return self.key.format(**format_params)
        else:
            return func.__name__

    @abstractmethod
    def from_cache(self, key):
        pass

    @abstractmethod
    def to_cache(self, key: str, value, time: timedelta):
        pass

    @abstractmethod
    def invalidate_cache(self, key: str):
        pass

