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
                # Surface which constraint actually violated; otherwise the
                # caller (and ops dashboards) see only "Conflict" with no
                # detail about which row / index collided.
                logger.warning(
                    'DuplicateErrorHandler caught IntegrityError in `%s`: %s',
                    func.__qualname__,
                    e.orig if getattr(e, 'orig', None) else e,
                )
                exception_message = build_function_key(self.message, func, *args, **kwargs) if self.message else None
                # Chain the original error so a debugger / Sentry sees both.
                raise StatusCodeException(HTTPStatus.CONFLICT, exception_message) from e

        return _wrapper
