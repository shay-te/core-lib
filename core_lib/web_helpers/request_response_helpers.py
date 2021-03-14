#
# RESPONSE
#
import json
from http import HTTPStatus
from http.client import responses
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
from core_lib.helpers.constants import MediaType, HttpHeaders

from django.http import HttpResponse
from flask import Flask


def response_status(status: int = HTTPStatus.OK.value):
    return response_json({}, status)


def response_ok(status: int = HTTPStatus.OK.value):
    return response_message('ok', status)


def response_message(message='', status: int = HTTPStatus.OK.value):
    if not message:
        message = responses[status] if status in responses else ''

    if status >= 500:
        data = {'error': message}
    else:
        data = {'message': message}

    return response_json(data, status)


def response_json(data: dict, status: int = HTTPStatus.OK.value):
    return generate_response(data, status, MediaType.APPLICATION_JSON)


def response_download_content(content, media_type: MediaType, file_name: str):
    headers = {HttpHeaders.CONTENT_DISPOSITION.value: f'attachment; filename="{file_name}"'}
    return generate_response(content,  HTTPStatus.OK.value, media_type, headers)


def generate_response(data, status, media_type: MediaType, headers: dict = {}):
    if not data:
        data = b''
    elif media_type == MediaType.APPLICATION_JSON:
        data = json.dumps(data)
    if WebHelpersUtils.get_server_type() == WebHelpersUtils.ServerType.DJANGO:
        return generate_response_django(data, status, media_type, headers)
    elif WebHelpersUtils.get_server_type() == WebHelpersUtils.ServerType.FLASK:
        return generate_response_flask(data, status, media_type, headers)


def generate_response_django(data, status, media_type: MediaType, headers: dict = {}):
    response = HttpResponse(content=data, status=status, content_type=media_type.value)
    for key, value in headers.items():
        response[key] = value
    return response


def generate_response_flask(data, status, media_type: MediaType, headers: dict = {}):
    response = Flask.response_class(response=data, status=status, mimetype=media_type.value)
    for key, value in headers.items():
        response.headers[key] = value
    return response

#
# HELPERS
#
def request_body_dict(request):
    if WebHelpersUtils.get_server_type() == WebHelpersUtils.ServerType.DJANGO:
        return json.loads(request.body.decode('utf-8'))
    elif WebHelpersUtils.get_server_type() == WebHelpersUtils.ServerType.FLASK:
        return request.json
