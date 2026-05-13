import logging
from functools import wraps
from http import HTTPStatus

from core_lib.error_handling.status_code_exception import StatusCodeException
from core_lib.helpers.func_utils import build_function_key

logger = logging.getLogger(__name__)


class NotFoundErrorHandler(object):
    def __init__(self, message: str = None):
        self.message = message

    def __call__(self, func, *args, **kwargs):
        @wraps(func)
        def _wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            # Use `is None` instead of `not result` so legitimate falsy
            # return values (0, '', [], {}, False) don't trigger a spurious
            # 404. SQLAlchemy's `.get()` and `.first()` return None on
            # miss, which is what we want to detect here.
            if result is None:
                logger.debug(f'NotFoundErrorHandler for function `{func.__qualname__}`.')
                exception_message = build_function_key(self.message, func, *args, **kwargs) if self.message else None
                raise StatusCodeException(HTTPStatus.NOT_FOUND, exception_message)
            return result

        return _wrapper
