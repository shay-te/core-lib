from functools import wraps

from core_lib.error_handling.status_code_exception import StatusCodeException
from core_lib.web_helpers.request_response_helpers import response_message


def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except StatusCodeException as n:
            return response_message(status=n.status_code)
        except BaseException as e:
            return response_message(status=500)
    return wrapper
