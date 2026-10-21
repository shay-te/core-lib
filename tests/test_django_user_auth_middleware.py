"""Django's UserAuthMiddleware refuses to start without settings.COOKIE_NAME, and puts the cookie's user on request.user."""
import unittest
from datetime import datetime, timedelta

from freezegun import freeze_time

from core_lib.session.jwt_token_handler import JWTTokenHandler
from core_lib.session.security_handler import SecurityHandler
from core_lib.session.user_security import UserSecurity

COOKIE_NAME = 'acme_cookie'
SECRET = 'acme-widget-secret-0123456789abcdef'   # 32+ bytes, so PyJWT has no key-length warning


class AcmeSecurity(UserSecurity):
    def secure_entry(self, request, session_obj, policies: list):
        return None

    def from_session_data(self, session_data: dict) -> dict:
        return {'user_id': session_data['user_id'], 'email': session_data['email']}

    def generate_session_data(self, user: dict) -> dict:
        return {'user_id': user['user_id'], 'email': user['email']}


def echo_request(request):
    # The view: the middleware passes the request on, so the test can look at what it set.
    return request


class TestDjangoUserAuthMiddleware(unittest.TestCase):

    def setUp(self):
        # Imported here: at module level the test loader touches Django's lazy settings before they are configured.
        from django.conf import settings
        if not settings.configured:
            settings.configure()
        # SecurityHandler holds one registration for the whole process: swap ours in, and put the old one back.
        self._registered = SecurityHandler.user_security
        SecurityHandler.user_security = None
        self.acme_security = AcmeSecurity(COOKIE_NAME, JWTTokenHandler(SECRET, timedelta(hours=1)))
        SecurityHandler.register(self.acme_security)

    def tearDown(self):
        SecurityHandler.user_security = self._registered

    def test_missing_or_empty_cookie_name_fails_at_startup(self):
        from django.conf import settings
        from django.core.exceptions import ImproperlyConfigured
        from django.test.utils import override_settings
        from core_lib.web_helpers.django.user_auth_middleware import UserAuthMiddleware

        with override_settings():
            del settings.COOKIE_NAME
            with self.assertRaises(ImproperlyConfigured) as missing:
                UserAuthMiddleware(lambda request: 'response')
        self.assertIn('COOKIE_NAME', str(missing.exception))

        with override_settings(COOKIE_NAME=''):
            with self.assertRaises(ImproperlyConfigured):
                UserAuthMiddleware(lambda request: 'response')

    def test_configured_cookie_name_starts_and_passes_requests_on(self):
        from django.test import RequestFactory
        from django.test.utils import override_settings
        from core_lib.web_helpers.django.user_auth_middleware import UserAuthMiddleware

        with override_settings(COOKIE_NAME='acme_cookie'):
            middleware = UserAuthMiddleware(lambda request: 'response')

            self.assertEqual('response', middleware(RequestFactory().get('/widgets')))

    def test_cookie_puts_the_user_on_the_request(self):
        from django.test import RequestFactory
        from django.test.utils import override_settings
        from core_lib.web_helpers.django.user_auth_middleware import UserAuthMiddleware

        token = self.acme_security.generate_session_data_token({'user_id': 7, 'email': 'reviewer@acme.com'})
        with override_settings(COOKIE_NAME=COOKIE_NAME):
            middleware = UserAuthMiddleware(echo_request)

            logged_in = middleware(RequestFactory().get('/widgets', HTTP_COOKIE=f'{COOKIE_NAME}={token}'))
            anonymous = middleware(RequestFactory().get('/widgets'))
            other_cookie = middleware(RequestFactory().get('/widgets', HTTP_COOKIE=f'other_cookie={token}'))

        self.assertEqual({'user_id': 7, 'email': 'reviewer@acme.com'}, logged_in.user)
        self.assertFalse(hasattr(anonymous, 'user'))      # no cookie: request.user is left alone
        self.assertFalse(hasattr(other_cookie, 'user'))

    def test_bad_or_expired_token_sets_none_and_never_blocks(self):
        from django.test import RequestFactory
        from django.test.utils import override_settings
        from core_lib.web_helpers.django.user_auth_middleware import UserAuthMiddleware

        token = self.acme_security.generate_session_data_token({'user_id': 7, 'email': 'reviewer@acme.com'})
        with override_settings(COOKIE_NAME=COOKIE_NAME):
            middleware = UserAuthMiddleware(echo_request)

            with self.assertLogs(level='ERROR'):
                garbage = middleware(RequestFactory().get('/widgets', HTTP_COOKIE=f'{COOKIE_NAME}=not-a-token'))
            with freeze_time(datetime.now() + timedelta(hours=1, seconds=1)):
                with self.assertLogs(level='ERROR'):
                    expired = middleware(RequestFactory().get('/widgets', HTTP_COOKIE=f'{COOKIE_NAME}={token}'))

        self.assertEqual('/widgets', garbage.path)   # the request still reached the view
        self.assertIsNone(garbage.user)
        self.assertIsNone(expired.user)
