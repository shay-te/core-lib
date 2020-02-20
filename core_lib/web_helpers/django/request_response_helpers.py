#
# RESPONSE
#
import http
import json
from http import HTTPStatus

from core_lib.web_helpers.django.response_generator import generate_response_django
from core_lib.web_helpers.flask.response_generator import generate_response_flask
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils


def response_ok():
    return response_message()


def response(status=HTTPStatus.OK.value):
    return response_message(status=status)


def response_message(message, status=HTTPStatus.OK.value):
    if not message:
        if status in http.client.responses:
            message = http.client.responses[status]
        else:
            message = _status_to_message(status)

    if status >= 500:
        data = {'error': message}
    else:
        data = {'message': message}

    if WebHelpersUtils.get_server_type() == WebHelpersUtils.ServerType.DJANGO:
        return generate_response_django(data, status)
    elif WebHelpersUtils.get_server_type() == WebHelpersUtils.ServerType.FLASK:
        return generate_response_flask(data, status)


def _status_to_message(status):
    if 200 <= status < 300:
        return 'Success'
    if 300 <= status < 400:
        return 'Redirection'
    if 400 <= status < 500:
        return 'Client error'
    if 400 <= status < 500:
        return 'Server error'
    return ''


#
# HELPERS
#


def request_body_dict(request):
    return json.loads(request.body.decode('utf-8'))

