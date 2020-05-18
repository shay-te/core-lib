from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from core_lib.session.security_handler import SecurityHandler


class UserAuthMiddleware(MiddlewareMixin):
    
    def process_request(self, request):
        assert hasattr(request, 'session'), (
            "The Django authentication middleware requires session middleware "
            "to be installed. Edit your MIDDLEWARE%s setting to insert "
            "'django.contrib.sessions.middleware.SessionMiddleware' before "
            "'django.contrib.auth.middleware.AuthenticationMiddleware'."
        ) % ("_CLASSES" if settings.MIDDLEWARE is None else "")
        if settings.COOKIE_NAME in request.COOKIES:
            request.__class__.user = SecurityHandler.get().generate_session_object(request.COOKIES[settings.COOKIE_NAME])
