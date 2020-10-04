import logging
from datetime import timedelta, datetime
from functools import wraps
from typing import Union

from core_lib.core_lib import CoreLib
from core_lib.helpers.func_utils import build_value_by_func_parameters
import parsedatetime

logger = logging.getLogger(__name__)
parse_datetime_calendar = parsedatetime.Calendar()


def _parse_datetime(expire: str):
    expire_datetime, result = parse_datetime_calendar.parseDT(expire)
    if result == 0:
        raise ValueError('Unable to parse time expression `{}`'.format(expire))
    return datetime.utcnow() - expire_datetime.replace(hour=0, minute=0, second=0, microsecond=0)


class Cache(object):

    # key: The key used to store the value with, when no key specified the function.__qualname__ is used
    # expire: period of time when the value is expired, string will be parse `parsedatetime` and then now-parsed_result
    # invalidate : remove the value from the cache using the key
    # cache_client_name: what name to use to get the correct `CacheHandler`
    def __init__(self,
                 key: str = None,
                 max_key_length: int = 250,
                 expire: Union[timedelta, str] = None,
                 invalidate: bool = False,
                 cache_client_name: str = None):
        self.key = key
        self.max_key_length = max_key_length
        self.expire = expire
        self.invalidate = invalidate
        self.cache_client_name = cache_client_name

        # validate expire BEFORE USE, in a reason to promote errors to startup time
        if self.expire and isinstance(self.expire, str):
            _parse_datetime(expire)  # Will raise an error on wrong expression

    def __call__(self, func, *args, **kwargs):

        @wraps(func)
        def __wrapper(*args, **kwargs):
            cache_client = CoreLib.cache_factory.get(self.cache_client_name)
            key = build_value_by_func_parameters(self.key, func, *args, **kwargs)[:self.max_key_length]

            if self.invalidate:
                result = func(*args, **kwargs)
                # Invalidate the cache only after calling decorated function.
                # Reasons:
                # 1. make cached item available during the invalidate function rum
                # 2. On exception don't invalidate
                cache_client.invalidate_cache(key)
                return result
            else:
                result = cache_client.from_cache(key)
                if not result:
                    result = func(*args, **kwargs)
                if result:
                    expire = self.expire
                    if expire and isinstance(expire, str):
                        expire = _parse_datetime(expire)
                    cache_client.to_cache(key, result, expire)
                return result

        return __wrapper
