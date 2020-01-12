import json
from functools import wraps
from http import HTTPStatus

from django.http import HttpResponse
from django.shortcuts import redirect
from django.conf import settings
import logging

from core_lib.session.session_manager import SessionManager
from core_lib.web_helpers.constants_media_type import MediaType
from core_lib.web_helpers.exceptions import NotFoundException
from core_lib.web_helpers.request_response_helpers import _response_message


#
# DECORATORS
#

class RequireLogin(object):

    def __init__(self, login_url):
        if not login_url:
            raise ValueError('login_url is missing');
        self.login_url = login_url
        self.logger = logging.getLogger(str(RequireLogin))

    def __call__(self, func, *args, **kwargs):

        def __wrapper(request, *args, **kwargs):
            session_value = None
            if settings.COOKIE_NAME in request.COOKIES:
                token = request.COOKIES[settings.COOKIE_NAME]
                session_value = SessionManager.get().decode(token)

            if session_value and hasattr(request, 'user'):
                if request.user.id == session_value['user_id']:
                    try:
                        return func(request, *args, **kwargs)
                    except Exception as e:
                        self.logger.error('error while loading target page for controller entry name {}'.format(func.__name__), exc_info=True)
                        return ''
                return redirect(self.login_url)
            else:
                if self.login_url:
                    return redirect(self.login_url)
                else:
                    self.logger.debug('RequireLogin: unable to fing login_url will return 401')
                    return response(status=HTTPStatus.UNAUTHORIZED)
        return __wrapper

#
# RESPONSE
#


def response_ok():
    return response_message()


def response(status=HTTPStatus.OK):
    return response_message(status=status)


def response_message(message, status=HTTPStatus.OK):
    data = _response_message(message, status)
    return HttpResponse(json.dumps(data), status=status, content_type=MediaType.APPLICATION_JSON.value)


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


