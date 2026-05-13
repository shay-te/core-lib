import unittest
from unittest.mock import MagicMock, patch

from django.conf import settings as django_settings


class TestDjangoUserAuthMiddleware(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not django_settings.configured:
            django_settings.configure()
            django_settings.DEFAULT_CHARSET = 'utf-8'
        django_settings.COOKIE_NAME = 'my_cookie'

    def _build_middleware(self):
        from core_lib.web_helpers.django.user_auth_middleware import UserAuthMiddleware
        return UserAuthMiddleware(get_response=lambda r: r)

    def test_process_request_sets_user_when_cookie_present(self):
        with patch(
            'core_lib.web_helpers.django.user_auth_middleware.SecurityHandler'
        ) as mock_sh:
            mock_user_security = MagicMock()
            mock_user_security.token_to_session_object.return_value = {'id': 1}
            mock_sh.get.return_value = mock_user_security

            middleware = self._build_middleware()
            request = MagicMock()
            request.COOKIES = {'my_cookie': 'token-value'}
            middleware.process_request(request)
            self.assertEqual(request.user, {'id': 1})
            mock_user_security.token_to_session_object.assert_called_once_with('token-value')

    def test_process_request_no_cookie(self):
        with patch(
            'core_lib.web_helpers.django.user_auth_middleware.SecurityHandler'
        ) as mock_sh:
            middleware = self._build_middleware()
            request = MagicMock()
            request.COOKIES = {}
            del request.user
            middleware.process_request(request)
            mock_sh.get.assert_not_called()


class TestFlaskUserAuthMiddleware(unittest.TestCase):
    def test_call_with_cookie_sets_user(self):
        from core_lib.web_helpers.flask.user_auth_middleware import UserAuthMiddleware

        captured_environ = {}

        def wsgi_app(env, start):
            captured_environ.update(env)
            return [b'ok']

        with patch(
            'core_lib.web_helpers.flask.user_auth_middleware.SecurityHandler'
        ) as mock_sh:
            mock_user_security = MagicMock()
            mock_user_security.token_to_session_object.return_value = {'id': 1}
            mock_sh.get.return_value = mock_user_security

            mw = UserAuthMiddleware(wsgi_app, 'my_cookie')
            environ = {
                'REQUEST_METHOD': 'GET',
                'PATH_INFO': '/',
                'HTTP_COOKIE': 'my_cookie=token-value',
                'wsgi.url_scheme': 'http',
            }
            start_response = MagicMock()
            result = mw(environ, start_response)
            self.assertEqual(result, [b'ok'])
            self.assertEqual(captured_environ['user'], {'id': 1})

    def test_call_without_cookie_skips_user(self):
        from core_lib.web_helpers.flask.user_auth_middleware import UserAuthMiddleware

        captured_environ = {}

        def wsgi_app(env, start):
            captured_environ.update(env)
            return [b'ok']

        with patch(
            'core_lib.web_helpers.flask.user_auth_middleware.SecurityHandler'
        ) as mock_sh:
            mw = UserAuthMiddleware(wsgi_app, 'my_cookie')
            environ = {
                'REQUEST_METHOD': 'GET',
                'PATH_INFO': '/',
                'wsgi.url_scheme': 'http',
            }
            start_response = MagicMock()
            mw(environ, start_response)
            self.assertNotIn('user', captured_environ)
            mock_sh.get.assert_not_called()
