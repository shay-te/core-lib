import logging
from datetime import timedelta, datetime, timezone
from functools import wraps
from typing import Union
import parsedatetime

from core_lib.core_lib import CoreLib
from core_lib.helpers.func_utils import build_function_key


logger = logging.getLogger(__name__)
parse_datetime_calendar = parsedatetime.Calendar()


def parse(d_time: str) -> datetime:
    result_datetime, result = parse_datetime_calendar.parseDT(d_time)
    if result == 0:
        raise ValueError('Unable to parse time expression `{}`'.format(d_time))
    result_utc_datetime = datetime.fromtimestamp(result_datetime.timestamp(), tz=timezone.utc).replace(tzinfo=None)
    return result_utc_datetime


def _parse_datetime(expire: str) -> timedelta:
    return parse(expire) - datetime.utcnow()


def _get_expire(expire) -> timedelta:
    # validate expire BEFORE USE, in a reason to promote errors to startup time
    if expire and isinstance(expire, str):
        return _parse_datetime(expire)  # Will raise an error on wrong expression
    return expire


class Cache(object):

    # key: The key used to store the value with, when no key specified the function.__qualname__ is used
    # expire: period of time when the value is expired, string will be parse `parsedatetime` and then now-parsed_result
    # invalidate : remove the value from the cache using the key
    # handler: what name to use to get the correct `CacheHandler`
    def __init__(
        self,
        key: str = None,
        max_key_length: int = 250,
        expire: Union[timedelta, str] = None,
        invalidate: bool = False,
        handler_name: str = None,
        cache_empty_result: bool = True,
    ):
        self.key = key
        self.max_key_length = max_key_length
        self.invalidate = invalidate
        self.handler_name = handler_name
        self.expire = _get_expire(expire)
        self.cache_empty_result = cache_empty_result

    def __call__(self, func, *args, **kwargs):
        @wraps(func)
        def __wrapper(*args, **kwargs):
            cache_handler = CoreLib.cache_registry.get(self.handler_name)
            if not cache_handler:
                raise ValueError(f'CacheHandler by name {self.handler_name} was not found in `CoreLib.cache_registry`')
            key = build_function_key(self.key, func, *args, **kwargs)[: self.max_key_length].replace(' ', '_')

            if self.invalidate:
                result = func(*args, **kwargs)
                # Invalidate the cache only after calling decorated function.
                # Reasons:
                # 1. make cached item available during the invalidate function rum
                # 2. On exception don't invalidate
                cache_handler.delete(key)
                return result
            else:
                result = cache_handler.get(key)
                if result is None:
                    result = func(*args, **kwargs)
                    if (self.cache_empty_result and result is not None) or result:
                        cache_handler.set(key, result, _get_expire(self.expire))
                return result

        return __wrapper
