from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.deprecation import MiddlewareMixin

from core_lib.session.security_handler import SecurityHandler


class UserAuthMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        # Checked once at startup: without it, every request would fail with an AttributeError.
        if not getattr(settings, 'COOKIE_NAME', None):
            raise ImproperlyConfigured(
                'UserAuthMiddleware reads the session cookie named by settings.COOKIE_NAME; '
                'set it to the cookie_name you gave your UserSecurity'
            )
        super().__init__(get_response)

    def process_request(self, request):
        # assert hasattr(request, 'handler'), (
        #     "The Django authentication middleware requires handler middleware "
        #     "to be installed. Edit your MIDDLEWARE%s setting to insert "
        #     "'django.contrib.handler.middleware.SessionMiddleware' before "
        #     "'django.contrib.auth.middleware.UserAuthMiddleware'."
        # ) % ("_CLASSES" if settings.MIDDLEWARE is None else "")
        if settings.COOKIE_NAME in request.COOKIES:
            request.user = SecurityHandler.get().token_to_session_object(request.COOKIES[settings.COOKIE_NAME])
