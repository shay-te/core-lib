from functools import wraps

from core_lib.web_helpers.exceptions import NotFoundException


def null_response_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        if not response:
            raise NotFoundException('Not found')
        return response

    return wrapper
