"""Flask's UserAuthMiddleware puts the cookie's user in request.environ['user'], and with @RequireLogin runs a login flow."""
import unittest
from datetime import datetime, timedelta
from http import HTTPStatus

from flask import Flask, request
from freezegun import freeze_time

from core_lib.session.jwt_token_handler import JWTTokenHandler
from core_lib.session.security_handler import SecurityHandler
from core_lib.session.user_security import UserSecurity
from core_lib.web_helpers.decorators import HandleException
from core_lib.web_helpers.flask.require_login import RequireLogin
from core_lib.web_helpers.flask.user_auth_middleware import UserAuthMiddleware
from core_lib.web_helpers.request_response_helpers import request_body_dict, response_json, response_status
from core_lib.web_helpers.web_helpers_utils import WebHelpersUtils

COOKIE_NAME = 'acme_cookie'
SECRET = 'acme-widget-secret-0123456789abcdef'   # 32+ bytes, so PyJWT has no key-length warning
TOKEN_LIFETIME = timedelta(hours=1)

USERS = {
    'ada@acme.com': {'id': 1, 'email': 'ada@acme.com', 'role': 'admin', 'password': 'ada-password'},
    'reviewer@acme.com': {'id': 2, 'email': 'reviewer@acme.com', 'role': 'viewer', 'password': 'reviewer-password'},
}


def authenticate(email: str, password: str):
    user = USERS.get(email)
    return user if user and user['password'] == password else None


class SessionUser(object):
    def __init__(self, user_id: int, email: str, role: str):
        self.user_id = user_id
        self.email = email
        self.role = role


class AcmeSecurity(UserSecurity):
    def generate_session_data(self, user: dict) -> dict:
        return {'id': user['id'], 'email': user['email'], 'role': user['role']}

    def from_session_data(self, session_data: dict) -> SessionUser:
        return SessionUser(session_data['id'], session_data['email'], session_data['role'])

    def secure_entry(self, request, session_obj: SessionUser, policies: list):
        if session_obj is None:
            return response_status(HTTPStatus.UNAUTHORIZED)
        if policies and session_obj.role not in policies:
            return response_status(HTTPStatus.FORBIDDEN)
        return None


def build_app(view_calls: list) -> Flask:
    app = Flask('acme')
    app.wsgi_app = UserAuthMiddleware(app.wsgi_app, cookie_name=COOKIE_NAME)

    @app.route('/admin')
    @RequireLogin(policies=['admin'])
    @HandleException()
    def admin_dashboard():
        view_calls.append('admin_dashboard')
        return response_json({'dashboard': 'admin data', 'viewer': request.environ['user'].email})

    @app.route('/login', methods=['POST'])
    @HandleException()
    def login():
        body = request_body_dict(request)
        user = authenticate(body['email'], body['password'])
        if not user:
            return response_status(HTTPStatus.UNAUTHORIZED)
        response = response_json({'ok': True})
        response.set_cookie(COOKIE_NAME, SecurityHandler.get().generate_session_data_token(user), httponly=True)
        return response

    @app.route('/whoami')
    def whoami():
        if 'user' not in request.environ:
            return {'cookie': False}
        session_user = request.environ['user']
        return {'cookie': True, 'email': None if session_user is None else session_user.email}

    return app


class TestFlaskUserAuthMiddleware(unittest.TestCase):

    def setUp(self):
        # SecurityHandler and WebHelpersUtils each hold one value for the whole process: put the old ones back after.
        self._registered = SecurityHandler.user_security
        self._server_type = WebHelpersUtils.server_type
        SecurityHandler.user_security = None
        self.acme_security = AcmeSecurity(COOKIE_NAME, JWTTokenHandler(SECRET, TOKEN_LIFETIME))
        SecurityHandler.register(self.acme_security)
        WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)
        self.view_calls = []
        self.app = build_app(self.view_calls)

    def tearDown(self):
        SecurityHandler.user_security = self._registered
        WebHelpersUtils.server_type = self._server_type

    def _client_with_cookie(self, name: str, value: str):
        client = self.app.test_client()
        client.set_cookie(name, value)
        return client

    def test_cookie_user_goes_into_environ(self):
        token = self.acme_security.generate_session_data_token(USERS['ada@acme.com'])

        logged_in = self._client_with_cookie(COOKIE_NAME, token).get('/whoami')
        anonymous = self.app.test_client().get('/whoami')
        other_cookie = self._client_with_cookie('other_cookie', token).get('/whoami')

        self.assertEqual({'cookie': True, 'email': 'ada@acme.com'}, logged_in.get_json())
        self.assertEqual({'cookie': False}, anonymous.get_json())
        self.assertEqual({'cookie': False}, other_cookie.get_json())

    def test_bad_or_expired_token_sets_none_and_never_blocks(self):
        token = self.acme_security.generate_session_data_token(USERS['ada@acme.com'])

        with self.assertLogs(level='ERROR'):
            garbage = self._client_with_cookie(COOKIE_NAME, 'not-a-token').get('/whoami')
        with freeze_time(datetime.now() + TOKEN_LIFETIME + timedelta(seconds=1)):
            with self.assertLogs(level='ERROR'):
                expired = self._client_with_cookie(COOKIE_NAME, token).get('/whoami')

        self.assertEqual((200, {'cookie': True, 'email': None}), (garbage.status_code, garbage.get_json()))
        self.assertEqual((200, {'cookie': True, 'email': None}), (expired.status_code, expired.get_json()))

    def test_login_then_protected_view(self):
        admin = self.app.test_client()
        login = admin.post('/login', json={'email': 'ada@acme.com', 'password': 'ada-password'})
        self.assertEqual((200, {'ok': True}), (login.status_code, login.get_json()))
        self.assertIn('HttpOnly', login.headers['Set-Cookie'])

        dashboard = admin.get('/admin')
        self.assertEqual((200, {'dashboard': 'admin data', 'viewer': 'ada@acme.com'}), (dashboard.status_code, dashboard.get_json()))
        self.assertEqual(['admin_dashboard'], self.view_calls)

        viewer = self.app.test_client()
        viewer.post('/login', json={'email': 'reviewer@acme.com', 'password': 'reviewer-password'})
        forbidden = viewer.get('/admin')
        self.assertEqual((403, b''), (forbidden.status_code, forbidden.data))

        no_cookie = self.app.test_client().get('/admin')
        self.assertEqual((401, b''), (no_cookie.status_code, no_cookie.data))

        with freeze_time(datetime.now() + TOKEN_LIFETIME + timedelta(seconds=1)):
            with self.assertLogs(level='ERROR'):
                expired = admin.get('/admin')
        self.assertEqual((401, {'message': 'Unauthorized'}), (expired.status_code, expired.get_json()))

        with self.assertLogs(level='ERROR'):
            not_a_token = self._client_with_cookie(COOKIE_NAME, 'not-a-token').get('/admin')
        self.assertEqual((500, {'error': 'Internal Server Error'}), (not_a_token.status_code, not_a_token.get_json()))

        wrong_password = self.app.test_client().post('/login', json={'email': 'ada@acme.com', 'password': 'guess'})
        self.assertEqual((401, b''), (wrong_password.status_code, wrong_password.data))
        self.assertNotIn('Set-Cookie', wrong_password.headers)

        self.assertEqual(['admin_dashboard'], self.view_calls)   # no blocked request reached the view
