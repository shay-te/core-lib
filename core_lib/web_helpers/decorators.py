from functools import wraps
from http import HTTPStatus

from core_lib.web_helpers.status_code_exception import StatusCodeException
from core_lib.web_helpers.django.request_response_helpers import response_message


def null_response_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        if not response:
            raise StatusCodeException(HTTPStatus.NOT_FOUND.value)
        return response

    return wrapper


def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except StatusCodeException as n:
            return response_message(status=n.status_code)
        except BaseException as e:
            raise e
    return wrapper
