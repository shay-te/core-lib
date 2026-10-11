"""Django's UserAuthMiddleware refuses to start without settings.COOKIE_NAME, instead of failing every request."""
import unittest
from datetime import timedelta

from core_lib.session.jwt_token_handler import JWTTokenHandler
from core_lib.session.security_handler import SecurityHandler
from core_lib.session.user_security import UserSecurity

SECRET = 'acme-test-secret-of-at-least-32-bytes'
COOKIE = 'acme_cookie'


class AcmeSecurity(UserSecurity):
    def secure_entry(self, request, session_obj, policies: list):
        return None

    def from_session_data(self, session_data: dict):
        return {'id': session_data['id'], 'name': session_data['name']}

    def generate_session_data(self, obj) -> dict:
        return {'id': obj['id'], 'name': obj['name']}


class TestDjangoUserAuthMiddleware(unittest.TestCase):

    def setUp(self):
        # Imported here: at module level the test loader touches Django's lazy settings before they are configured.
        from django.conf import settings
        if not settings.configured:
            settings.configure()
        self._user_security = SecurityHandler.user_security
        SecurityHandler.user_security = AcmeSecurity(COOKIE, JWTTokenHandler(SECRET, timedelta(minutes=5)))

    def tearDown(self):
        SecurityHandler.user_security = self._user_security

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

    def test_reads_the_user_from_the_configured_cookie(self):
        from django.test import RequestFactory
        from django.test.utils import override_settings
        from core_lib.web_helpers.django.user_auth_middleware import UserAuthMiddleware

        with override_settings(COOKIE_NAME=COOKIE):
            middleware = UserAuthMiddleware(lambda request: 'response')

            anonymous = RequestFactory().get('/widgets')
            self.assertEqual('response', middleware(anonymous))
            self.assertFalse(hasattr(anonymous, 'user'))

            signed_in = RequestFactory().get('/widgets')
            signed_in.COOKIES[COOKIE] = SecurityHandler.get().generate_session_data_token({'id': 7, 'name': 'reviewer'})
            self.assertEqual('response', middleware(signed_in))
            self.assertEqual({'id': 7, 'name': 'reviewer'}, signed_in.user)

            other_cookie = RequestFactory().get('/widgets')
            other_cookie.COOKIES['other_cookie'] = signed_in.COOKIES[COOKIE]
            middleware(other_cookie)
            self.assertFalse(hasattr(other_cookie, 'user'))
