import logging
from functools import wraps
from http import HTTPStatus

from core_lib.error_handling.status_code_exception import StatusCodeException
from core_lib.helpers.func_utils import build_value_by_func_parameters

logger = logging.getLogger(__name__)


class NotFoundErrorHandler(object):

    def __init__(self, message: str = None):
        self.message = message

    def __call__(self, func, *args, **kwargs):

        @wraps(func)
        def _wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if not result:
                logger.debug("NotFoundErrorHandler for function `{}`.".format(func.__qualname__))
                message = None
                if self.message:
                    message = build_value_by_func_parameters(self.message, func, *args, **kwargs)
                raise StatusCodeException(HTTPStatus.NOT_FOUND.value, message)
            return result

        return _wrapper

