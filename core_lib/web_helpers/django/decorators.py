import json

from django.http import HttpResponse
from django.shortcuts import redirect
from django.conf import settings
import logging

from core_lib.session.session_manager import SessionManager
from core_lib.web_helpers.constants_media_type import MediaType

#
# SESSION
#


def build_page_context(request):
    return {
        'user_id': request.user.id,
        'facebook_id': request.user.facebook_id,
        'csrf_token': request.META['CSRF_COOKIE'] if 'CSRF_COOKIE' in request.META else ''
    }


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
                if request.user.id == session_value['user_id'] :
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
                    return response_unauthorized()
        return __wrapper

#
# RESPONSE
#


def response_ok():
    return response_msg('ok')


def response_unauthorized():
    return response_msg('401 Unauthorized', status=401)


def response_msg(message, status=200, is_error=False):
    if message is None and 200 <= status < 300:
        message = 'ok'

    if is_error:
        status = 500
        data = {'error': message}
    else:
        data = {'message': message}

    return response_json(data, status)


def response_json(data, status=200):
    return HttpResponse(json.dumps(data), status=status, content_type=MediaType.APPLICATION_JSON.value)


#
# HELPERS
#


def request_body_dict(request):
    return json.loads(request.body.decode('utf-8'))
