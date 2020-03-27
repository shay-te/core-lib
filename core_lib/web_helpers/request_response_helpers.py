#
# RESPONSE
#
import json
from http import HTTPStatus
from http.client import responses

from core_lib.web_helpers.django.response_generator import generate_response_django
from core_lib.web_helpers.flask.response_generator import generate_response_flask
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils


def response_ok():
    return response_message()


def response(status=HTTPStatus.OK.value):
    return response_message(status=status)


def response_message(message, status=HTTPStatus.OK.value):
    if not message:
        message = responses[status] if status in responses else ''

    if status >= 500:
        data = {'error': message}
    else:
        data = {'message': message}

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
