#
# RESPONSE
#
import json
from http import HTTPStatus
from http.client import responses

from core_lib.web_helpers.django.response_generator import generate_response_django
from core_lib.web_helpers.flask.response_generator import generate_response_flask
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils


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
    if WebHelpersUtils.get_server_type() == WebHelpersUtils.ServerType.DJANGO:
        return generate_response_django(data, status)
    elif WebHelpersUtils.get_server_type() == WebHelpersUtils.ServerType.FLASK:
        return generate_response_flask(data, status)


#
# HELPERS
#
def request_body_dict(request):
    if WebHelpersUtils.get_server_type() == WebHelpersUtils.ServerType.DJANGO:
        return json.loads(request.body.decode('utf-8'))
    elif WebHelpersUtils.get_server_type() == WebHelpersUtils.ServerType.FLASK:
        return request.json
