from http import HTTPStatus

from django.shortcuts import redirect
from django.conf import settings
import logging
from core_lib.session.session_manager import SessionManager
from core_lib.web_helpers.django.request_response_helpers import response


class RequireLogin(object):

    def __init__(self, login_url):
        if not login_url:
            raise ValueError('login_url is missing');
        self.login_url = login_url
        self.logger = logging.getLogger(self.__class__.__name__)

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

