import logging
from functools import wraps
from http import HTTPStatus

from core_lib.error_handling.status_code_exception import StatusCodeException

logger = logging.getLogger(__name__)


def empty_result_error_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if not result:
            logger.warning("Empty result when calling `{}`.".format(func.__qualname__))
            raise StatusCodeException(HTTPStatus.NOT_FOUND.value)
        return result

    return wrapper
