import json
from functools import wraps
from http import HTTPStatus
from flask import Flask

from core_lib.web_helpers.exceptions import NotFoundException


def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NotFoundException as n:
            return response_message("Not found", status=HTTPStatus.NOT_FOUND)
        except BaseException as e:
            raise e
    return wrapper

def response_message(message, status: int = HTTPStatus.OK):
    return response_content({'message': message}, status=status)


def response_content(content: dict, status: int = HTTPStatus.OK):
    return Flask.response_class(response=json.dumps(content),
                              status=status,
                              mimetype='application/json')