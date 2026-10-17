#
# RESPONSE
#
import json
from http import HTTPStatus
from http.client import responses
from typing import Union

from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
from core_lib.helpers.constants import MediaType, HttpHeaders

from django.http import HttpResponse
from flask import Flask
from starlette.responses import Response as StarletteResponse


def response_status(status: int = HTTPStatus.OK.value):
    return generate_response(None, status)


def response_ok(status: int = HTTPStatus.OK.value):
    return response_message('ok', status)


def response_error(message='', status: int = HTTPStatus.INTERNAL_SERVER_ERROR.value):
    if not message:
        message = responses[status] if status in responses else ''
    return response_json({'error': message}, status)


def response_message(message='', status: int = HTTPStatus.OK.value):
    if not message:
        message = responses[status] if status in responses else ''

    if status >= 500:
        data = {'error': message}
    else:
        data = {'message': message}

    return response_json(data, status)


def response_json(data: Union[dict, list], status: int = HTTPStatus.OK.value):
    return generate_response(data, status, MediaType.APPLICATION_JSON)


def response_download_content(content, media_type: MediaType, file_name: str):
    headers = {HttpHeaders.CONTENT_DISPOSITION.value: f'attachment; filename="{file_name}"'}
    return generate_response(content, HTTPStatus.OK.value, media_type, headers)


def generate_response(data, status, media_type: MediaType = MediaType.TEXT_HTML, headers: dict = {}):
    if data is None:
        data = b''
    elif media_type == MediaType.APPLICATION_JSON:
        data = json.dumps(data)
    if WebHelpersUtils.get_server_type() == WebHelpersUtils.ServerType.DJANGO:
        return generate_response_django(data, status, media_type, headers)
    elif WebHelpersUtils.get_server_type() == WebHelpersUtils.ServerType.FLASK:
        return generate_response_flask(data, status, media_type, headers)
    elif WebHelpersUtils.get_server_type() == WebHelpersUtils.ServerType.FASTAPI:
        return generate_response_fastapi(data, status, media_type, headers)


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


def generate_response_fastapi(data, status, media_type: MediaType, headers: dict = None):
    # Starlette Response — works for FastAPI views and middlewares.
    # FastAPI accepts these directly as view return values.
    if headers is None:
        headers = {}
    # IntEnum compatibility — Starlette accepts int but `status_code` is
    # explicitly typed int and HTTPStatus members satisfy that.
    response = StarletteResponse(
        content=data,
        status_code=int(status),
        media_type=media_type.value,
    )
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
    elif WebHelpersUtils.get_server_type() == WebHelpersUtils.ServerType.FASTAPI:
        # FastAPI's normal pattern is `await request.json()` inside an async
        # view. Inside this sync helper we expect callers to have pre-read
        # the body (e.g. via a sync wrapper, or by passing `request.json()`
        # already-resolved). Accept both shapes for ergonomics.
        body = request.body if isinstance(request.body, (bytes, bytearray)) else None
        if body is not None:
            return json.loads(body.decode('utf-8'))
        return None
