from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from core_lib.session.SessionUser import SessionUser
from core_lib.session.session_manager import SessionManager


class UserAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        assert hasattr(request, 'session'), (
            "The authentication middleware requires session middleware "
            "to be installed. Edit your MIDDLEWARE%s setting to insert "
            "'django.contrib.sessions.middleware.SessionMiddleware' before "
            "'django.contrib.auth.middleware.AuthenticationMiddleware'."
        ) % ("_CLASSES" if settings.MIDDLEWARE is None else "")
        if settings.COOKIE_NAME in request.COOKIES:
            token = request.COOKIES[settings.COOKIE_NAME]
            if token:
                user_info = SessionManager.get().decode(token)
                if user_info:
                    request.__class__.user = SessionUser(user_info['user_id'], user_info['facebook_id'], token)
