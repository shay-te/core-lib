import logging
from functools import wraps

from core_lib.error_handling.status_code_exception import StatusCodeException
from core_lib.web_helpers.request_response_helpers import response_message

logger = logging.getLogger(__name__)


def handle_exceptions(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except StatusCodeException as n:
            logger.exception(n)
            return response_message(status=n.status_code)
        except BaseException as bx:
            logger.exception(bx)
            return response_message(status=500)

    return wrapper
