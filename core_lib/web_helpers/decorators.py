import logging
from functools import wraps
from http import HTTPStatus

from jwt import ExpiredSignatureError

from core_lib.error_handling.status_code_exception import StatusCodeException
from core_lib.web_helpers.request_response_helpers import response_message

logger = logging.getLogger(__name__)


def handle_exception(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except StatusCodeException as n:
        logger.error(f'handle_exception got StatusCodeException error for function `{func}`')
        logger.exception(n, exc_info=True)
        return response_message(status=n.status_code)
    except AssertionError as n:
        logger.error(f'handle_exception got AssertionError error for function `{func}`')
        logger.exception(n, exc_info=True)
        return response_message(status=HTTPStatus.INTERNAL_SERVER_ERROR)
    except ExpiredSignatureError as ese:
        logger.error(f'handle_exception got ExpiredSignatureError error for function `{func}`')
        logger.exception(ese, exc_info=True)
        return response_message(status=HTTPStatus.UNAUTHORIZED)
    except BaseException as bx:
        logger.error(f'handle_exception got BaseException error for function `{func}`')
        logger.exception(bx, exc_info=True)
        return response_message(status=HTTPStatus.INTERNAL_SERVER_ERROR)


class HandleException(object):
    def __call__(self, func, *args, **kwargs):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return handle_exception(func, *args, **kwargs)

        return wrapper
