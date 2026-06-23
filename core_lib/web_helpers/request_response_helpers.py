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
    """
    Generate a downloadable file response with the specified content and filename.
    
    Returns:
    	A response object configured as a file attachment with the specified media type and filename.
    """
    headers = {HttpHeaders.CONTENT_DISPOSITION.value: f'attachment; filename="{file_name}"'}
    return generate_response(content, HTTPStatus.OK.value, media_type, headers)


def generate_response(data, status, media_type: MediaType = MediaType.TEXT_HTML, headers: dict = None):
    """
    Generate an HTTP response for the current web framework.
    
    Normalizes the response data by converting None to empty bytes and serializing to a JSON string if the media type is APPLICATION_JSON. Returns a framework-specific response object.
    
    Parameters:
    	data: Response body content. Converted to empty bytes if None; serialized to JSON string if media_type is APPLICATION_JSON.
    	status (int): HTTP status code.
    	media_type (MediaType): Content-Type of the response. Defaults to TEXT_HTML.
    	headers (dict): Custom HTTP headers to include in the response. Defaults to an empty dict if not provided.
    
    Returns:
    	A framework-specific HTTP response object (Django HttpResponse or Flask Response).
    """
    if headers is None:
        headers = {}
    if data is None:
        data = b''
    elif media_type == MediaType.APPLICATION_JSON:
        data = json.dumps(data)
    if WebHelpersUtils.get_server_type() == WebHelpersUtils.ServerType.DJANGO:
        return generate_response_django(data, status, media_type, headers)
    elif WebHelpersUtils.get_server_type() == WebHelpersUtils.ServerType.FLASK:
        return generate_response_flask(data, status, media_type, headers)


def generate_response_django(data, status, media_type: MediaType, headers: dict = None):
    """
    Create a Django HTTP response with the given data and status code.
    
    Parameters:
    	data: The response body content.
    	headers (dict): Optional custom headers to add to the response.
    
    Returns:
    	HttpResponse: A Django HTTP response object.
    """
    if headers is None:
        headers = {}
    response = HttpResponse(content=data, status=status, content_type=media_type.value)
    for key, value in headers.items():
        response[key] = value
    return response


def generate_response_flask(data, status, media_type: MediaType, headers: dict = None):
    """
    Create a Flask HTTP response with the specified content, status code, media type, and headers.
    
    Parameters:
    	data: The response body content
    	status (int): The HTTP status code
    	media_type (MediaType): The response content type
    	headers (dict): Custom HTTP headers to include
    
    Returns:
    	A Flask response object
    """
    if headers is None:
        headers = {}
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
