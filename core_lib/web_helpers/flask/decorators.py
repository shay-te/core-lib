import json
from functools import wraps
from http import HTTPStatus
from flask import Flask

from core_lib.web_helpers.constants_media_type import MediaType
from core_lib.web_helpers.exceptions import NotFoundException
from core_lib.web_helpers.request_response_helpers import _response_message


def response_ok():
    return response_message()


def response(status=HTTPStatus.OK):
    return response_message(status=status)


def response_message(message, status=HTTPStatus.OK):
    data = _response_message(message, status)
    return Flask.response_class(response=json.dumps(data),
                                  status=status,
                                  mimetype=MediaType.APPLICATION_JSON.value)


def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NotFoundException as n:
            return response_message(status=HTTPStatus.NOT_FOUND)
        except BaseException as e:
            raise e
    return wrapper


