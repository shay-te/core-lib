import json
from http import HTTPStatus
from flask import Flask


def response_message(message, status: int = HTTPStatus.OK):
    return response_content({'message': message}, status=status)


def response_content(content: dict, status: int = HTTPStatus.OK):
    return Flask.response_class(response=json.dumps(content),
                              status=status,
                              mimetype='application/json')