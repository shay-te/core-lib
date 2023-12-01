import logging
from functools import wraps
from http import HTTPStatus

from sqlalchemy import exc

from core_lib.error_handling.status_code_exception import StatusCodeException
from core_lib.helpers.func_utils import build_function_key

logger = logging.getLogger(__name__)


class DuplicateErrorHandler(object):
    def __init__(self, message: str = None):
        self.message = message

    def __call__(self, func, *args, **kwargs):
        @wraps(func)
        def _wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exc.IntegrityError as e:
                logger.debug(f'DuplicateErrorHandler for function `{func.__qualname__}`.')
                exception_message = build_function_key(self.message, func, *args, **kwargs) if self.message else None
                raise StatusCodeException(HTTPStatus.CONFLICT, exception_message)

        return _wrapper
