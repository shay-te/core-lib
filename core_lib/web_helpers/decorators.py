import logging
from functools import wraps
from http import HTTPStatus

from core_lib.error_handling.status_code_exception import StatusCodeException
from core_lib.web_helpers.request_response_helpers import response_message

logger = logging.getLogger(__name__)


def handle_exceptions(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except StatusCodeException as n:
            logger.error('handle_exceptions got error for function `{}`'.format(func))
            logger.exception(n, exc_info=True)
            return response_message(status=n.status_code)
        except AssertionError as n:
            logger.error('handle_exceptions got error for function `{}`'.format(func))
            logger.exception(n, exc_info=True)
            return response_message(status=HTTPStatus.NOT_ACCEPTABLE.value)
        except BaseException as bx:
            logger.error('handle_exceptions got error for function `{}`'.format(func))
            logger.exception(bx, exc_info=True)
            return response_message(status=500)

    return wrapper
