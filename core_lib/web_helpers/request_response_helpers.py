
#
# RESPONSE
#
import json
from functools import wraps
from http import HTTPStatus

from core_lib.web_helpers.exceptions import NotFoundException


def _response_ok():
    return _response_message()


def _response_message(message, status=HTTPStatus.OK):
    if not message:
        message = _status_to_message(status)

    if status >= 500:
        data = {'error': message}
    else:
        data = {'message': message}

    return data


def _status_to_message(status):
    if 200 <= status < 300:
        return 'ok'
    elif status == 401:
        return '401 Unauthorized'
    elif status == 404:
        return '401 Not Found'

    return ''


#
# HELPERS
#


def request_body_dict(request):
    return json.loads(request.body.decode('utf-8'))

