import secrets
import unittest
from datetime import timedelta, datetime, timezone
from http import HTTPStatus
from typing import Callable

import jwt
from django.http import HttpRequest
from flask import request as flask_request, Flask
from flask_wtf.csrf import CSRFProtect
from freezegun import freeze_time
from werkzeug.http import dump_cookie
from core_lib.cache.cache_handler_ram import CacheHandlerRam
from core_lib.core_lib import CoreLib
from core_lib.data_transform.result_to_dict import result_to_dict
from core_lib.session.jwt_token_handler import JWTTokenHandler
from core_lib.session.security_handler import SecurityHandler
from core_lib.session.token_handler import TokenHandler
from core_lib.session.user_security import UserSecurity
from core_lib.web_helpers.decorators import HandleException
from core_lib.web_helpers.django.require_login import RequireLogin as RequireLoginDjango
from core_lib.web_helpers.flask.require_login import RequireLogin as RequireLoginFlask
from core_lib.web_helpers.request_response_helpers import response_status
from core_lib.web_helpers.require_login_helper import require_login
from core_lib.web_helpers.web_helpers_utils import WebHelpersUtils
from tests.test_data.test_user_security_utils import CustomerSecurity, SessionUser, user_data_access, User, has_access

# The names of the views that actually ran, so a test can tell "the view ran"
# from "the security check answered instead of the view".
view_calls = []


def ok_view(*args):
    view_calls.append('ok_view')
    return response_status(HTTPStatus.OK)

# SECURITY HANDLER REGISTER
secret_key = 'super-secret'
cookie_name = 'my_cookie_name'
security_handler = CustomerSecurity(cookie_name, secret_key, timedelta(seconds=30))
SecurityHandler.register(security_handler)
widget_secret = 'acme-widget-secret-0123456789abcdef'   # 32+ bytes, so PyJWT has no key-length warning


class SessionStoreTokenHandler(TokenHandler):
    # Opaque tokens: the session stays on the server, and the cookie holds only a random key to it.
    def __init__(self):
        self._sessions = {}

    def encode(self, message: dict):
        token = secrets.token_hex(16)
        self._sessions[token] = dict(message)
        return token

    def decode(self, encoded):
        return self._sessions.get(encoded)


class WidgetSecurity(UserSecurity):
    # Lets every request in, and keeps the policies each check was given.
    def __init__(self, token_handler: TokenHandler):
        UserSecurity.__init__(self, cookie_name, token_handler)
        self.policies_seen = []

    def secure_entry(self, request, session_obj, policies: list):
        self.policies_seen.append(policies)
        return None

    def from_session_data(self, session_data: dict) -> SessionUser:
        return SessionUser(session_data['id'], session_data['role'], session_data['status'])

    def generate_session_data(self, user) -> dict:
        return {'id': user['id'], 'role': user['role'], 'status': user['status']}


class TestUserSecurity(unittest.TestCase):
    @classmethod
    def setUp(cls):
        CoreLib.cache_registry.unregister('test_user_security')

        cls.user_admin = result_to_dict(
            user_data_access.create({'username': 'admin', 'email': 'admin@def.com', 'role': User.PolicyRoles.ADMIN})
        )
        cls.user_delete = result_to_dict(
            user_data_access.create({'username': 'delete', 'email': 'delete@def.com', 'role': User.PolicyRoles.DELETE})
        )
        cls.user_create = result_to_dict(
            user_data_access.create({'username': 'create', 'email': 'create@def.com', 'role': User.PolicyRoles.CREATE})
        )
        cls.user_update = result_to_dict(
            user_data_access.create({'username': 'update', 'email': 'update@def.com', 'role': User.PolicyRoles.UPDATE})
        )
        cls.user_user = result_to_dict(
            user_data_access.create({'username': 'user', 'email': 'user@def.com', 'role': User.PolicyRoles.USER})
        )
        cls.user_ban = result_to_dict(
            user_data_access.create(
                {'username': 'user_ban', 'email': 'user_ban@def.com', 'role': User.PolicyRoles.USER, 'status': User.Status.BAN}
            )
        )
        cls.user_inactive = result_to_dict(
            user_data_access.create(
                {
                    'username': 'user_inactive',
                    'email': 'user_inactive@def.com',
                    'role': User.PolicyRoles.USER,
                    'status': User.Status.NOT_ACTIVE,
                }
            )
        )

        exp = datetime.now() + timedelta(seconds=30)
        cls.user_admin.update({'exp': exp})
        cls.user_delete.update({'exp': exp})
        cls.user_create.update({'exp': exp})
        cls.user_update.update({'exp': exp})
        cls.user_user.update({'exp': exp})
        cls.user_ban.update({'exp': exp})
        cls.user_inactive.update({'exp': exp})

        CoreLib.cache_registry.register('test_user_security', CacheHandlerRam())
        app = Flask(__name__)
        csrf = CSRFProtect()
        csrf.init_app(app)
        cls.app = app

    def test_security_handler_holds_one_registration(self):
        registered = SecurityHandler.user_security
        try:
            with self.assertRaises(ValueError) as twice:
                SecurityHandler.register(CustomerSecurity('other_cookie', secret_key, timedelta(seconds=30)))
            self.assertEqual('SecurityHandler already set', str(twice.exception))
            self.assertIs(security_handler, SecurityHandler.get())   # the first registration is kept

            SecurityHandler.user_security = None   # a process that never registered
            with self.assertRaises(ValueError) as unset:
                SecurityHandler.get()
            self.assertEqual('SecurityHandler was not set', str(unset.exception))
        finally:
            SecurityHandler.user_security = registered

    def test_require_login_without_policies_passes_an_empty_list(self):
        from django.conf import settings
        from django.test import RequestFactory
        if not settings.configured:
            settings.configure()
        registered, server_type = SecurityHandler.user_security, WebHelpersUtils.server_type
        widget_security = WidgetSecurity(JWTTokenHandler(widget_secret, timedelta(seconds=30)))
        SecurityHandler.user_security = widget_security
        try:
            WebHelpersUtils.init(WebHelpersUtils.ServerType.DJANGO)

            @RequireLoginDjango()
            def list_widgets_django(request):
                return response_status(HTTPStatus.OK)

            self.assertEqual(200, list_widgets_django(RequestFactory().get('/widgets')).status_code)

            WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)

            @RequireLoginFlask()
            def list_widgets_flask():
                return response_status(HTTPStatus.OK)

            with self.app.test_request_context('/widgets'):
                self.assertEqual(200, list_widgets_flask().status_code)
        finally:
            SecurityHandler.user_security, WebHelpersUtils.server_type = registered, server_type

        self.assertEqual([[], []], widget_security.policies_seen)

    def test_view_errors_under_require_login(self):
        # @RequireLogin logs a view's error and returns nothing, so Flask answers with its own HTML 500.
        # With @HandleException() underneath, the client gets the JSON error response instead.
        server_type = WebHelpersUtils.server_type
        WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)
        app = Flask('acme')

        @app.get('/widgets')
        @RequireLoginFlask()
        def list_widgets():
            raise RuntimeError('widget store is down')

        @app.get('/gadgets')
        @RequireLoginFlask()
        @HandleException()
        def list_gadgets():
            raise RuntimeError('gadget store is down')

        client = app.test_client()
        try:
            with self.assertLogs('acme', level='ERROR') as flask_logs:
                with self.assertLogs('core_lib.web_helpers.require_login_helper', level='ERROR') as logs:
                    widgets = client.get('/widgets')
            with self.assertLogs('core_lib.web_helpers.decorators', level='ERROR'):
                gadgets = client.get('/gadgets')
        finally:
            WebHelpersUtils.server_type = server_type

        self.assertEqual(500, widgets.status_code)
        self.assertEqual('text/html; charset=utf-8', widgets.content_type)
        self.assertEqual(
            ['error while loading target page for controller entry name `list_widgets`'],
            [record.getMessage() for record in logs.records],
        )
        self.assertIsInstance(logs.records[0].exc_info[1], RuntimeError)
        self.assertIn('did not return a valid response', str(flask_logs.records[0].exc_info[1]))
        self.assertEqual(500, gadgets.status_code)
        self.assertEqual({'error': 'Internal Server Error'}, gadgets.get_json())

    def test_token_to_session_object_never_raises(self):
        user = {'id': 7, 'role': User.PolicyRoles.UPDATE.value, 'status': User.Status.ACTIVE.value}
        jwt_security = WidgetSecurity(JWTTokenHandler(widget_secret, timedelta(seconds=30)))
        token = jwt_security.generate_session_data_token(user)

        session_user = jwt_security.token_to_session_object(token)
        self.assertEqual((7, 4, 1), (session_user.id, session_user.role, session_user.status))

        with freeze_time(datetime.now() + timedelta(seconds=31)):
            with self.assertLogs(level='ERROR') as expired_logs:
                self.assertIsNone(jwt_security.token_to_session_object(token))
        self.assertEqual(
            [('JWTTokenHandler', 'Signature has expired'), ('WidgetSecurity', 'Signature has expired')],
            [(record.name, record.getMessage()) for record in expired_logs.records],
        )

        forged = jwt.encode(user, 'another-acme-secret-0123456789abcdef')
        for bad_token in ('not-a-token', forged):
            with self.assertLogs('WidgetSecurity', level='ERROR'):
                with self.assertLogs('JWTTokenHandler', level='ERROR'):
                    self.assertIsNone(jwt_security.token_to_session_object(bad_token))

        store_security = WidgetSecurity(SessionStoreTokenHandler())
        stored_token = store_security.generate_session_data_token(user)
        self.assertEqual(7, store_security.token_to_session_object(stored_token).id)
        with self.assertNoLogs(level='ERROR'):   # an unknown token is an absent session, not an error
            self.assertIsNone(store_security.token_to_session_object('unknown-token'))

    def test_has_access(self):
        self.assertTrue(
            has_access(security_handler.from_session_data(self.user_admin), [User.PolicyRoles.ADMIN, User.Status.ACTIVE])
        )
        self.assertTrue(has_access(security_handler.from_session_data(self.user_delete), [User.PolicyRoles.DELETE]))
        self.assertTrue(has_access(security_handler.from_session_data(self.user_create), [User.PolicyRoles.CREATE]))
        self.assertTrue(has_access(security_handler.from_session_data(self.user_update), [User.PolicyRoles.UPDATE]))
        self.assertTrue(has_access(security_handler.from_session_data(self.user_user), [User.PolicyRoles.USER]))

        self.assertFalse(has_access(security_handler.from_session_data(self.user_user), [User.PolicyRoles.ADMIN]))
        self.assertFalse(has_access(security_handler.from_session_data(self.user_update), [User.PolicyRoles.DELETE]))
        self.assertFalse(has_access(security_handler.from_session_data(self.user_user), [User.PolicyRoles.CREATE]))
        self.assertFalse(
            has_access(security_handler.from_session_data(self.user_admin), [User.PolicyRoles.ADMIN, User.Status.NOT_ACTIVE])
        )

        self.assertTrue(
            has_access(security_handler.from_session_data(self.user_delete), [User.PolicyRoles.UPDATE, User.Status.ACTIVE])
        )
        self.assertTrue(
            has_access(security_handler.from_session_data(self.user_update), [User.PolicyRoles.USER, User.Status.ACTIVE])
        )
        self.assertTrue(
            has_access(security_handler.from_session_data(self.user_admin), [User.PolicyRoles.CREATE, User.Status.ACTIVE])
        )
        self.assertTrue(
            has_access(security_handler.from_session_data(self.user_create), [User.PolicyRoles.UPDATE, User.Status.ACTIVE])
        )
        self.assertTrue(
            has_access(security_handler.from_session_data(self.user_delete), [User.PolicyRoles.CREATE, User.Status.ACTIVE])
        )

        self.assertTrue(has_access(security_handler.from_session_data(self.user_admin), [User.Status.ACTIVE]))
        self.assertTrue(has_access(security_handler.from_session_data(self.user_delete), [User.Status.ACTIVE]))
        self.assertTrue(has_access(security_handler.from_session_data(self.user_create), [User.Status.ACTIVE]))
        self.assertTrue(has_access(security_handler.from_session_data(self.user_update), [User.Status.ACTIVE]))
        self.assertTrue(has_access(security_handler.from_session_data(self.user_user), [User.Status.ACTIVE]))

    def test_session_data(self):
        time_stamp = datetime.now(timezone.utc).timestamp()
        user = result_to_dict(user_data_access.get(1))
        user_session = SecurityHandler.get().generate_session_data_token(user)
        decoded_dict = jwt.decode(user_session, options={"verify_signature": False})

        self.assertIsInstance(decoded_dict, dict)
        self.assertEqual(decoded_dict['id'], user['id'])
        self.assertEqual(decoded_dict['email'], user['email'])
        self.assertGreater(decoded_dict['exp'], time_stamp)
        self.assertEqual(int(decoded_dict['exp']), int(time_stamp) + 30)

    def test_secure_django(self):
        # DJANGO INIT
        # Imported here: at module level the lazy `settings` object is touched by the test loader
        # before anything configures Django, which fails when this module runs on its own.
        from django.conf import settings
        if not settings.configured:
            settings.configure()
            settings.DEFAULT_CHARSET = 'utf-8'
        WebHelpersUtils.init(WebHelpersUtils.ServerType.DJANGO)

        self._test_secure_entry()
        self._test_expiry()
        self._test_decorator_django()

    def test_secure_flask(self):
        # FLASK INIT
        WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)

        self._test_secure_entry()
        self._test_expiry()
        self._test_decorator_flask()

    def _require_login(self, user: dict, policies: list, decorated_function: Callable[[], object] = None):
        token = jwt.encode(user, secret_key)
        if WebHelpersUtils.get_server_type() == WebHelpersUtils.ServerType.FLASK:
            header = dump_cookie(cookie_name, token)
            with self.app.test_request_context(environ_base={'HTTP_COOKIE': header}):
                self.assertEqual(flask_request.cookies[cookie_name], token)
                if decorated_function:
                    return decorated_function()
                return require_login(flask_request, policies, ok_view)
        else:
            django_request = HttpRequest
            django_request.COOKIES = {cookie_name: token}
            self.assertEqual(django_request.COOKIES[cookie_name], token)
            if decorated_function:
                return decorated_function(django_request)
            return require_login(django_request, policies, ok_view)

    def _test_secure_entry(self):

        POLICIES_ADMIN = [User.PolicyRoles.ADMIN, User.Status.ACTIVE]
        POLICIES_DELETE = [User.PolicyRoles.DELETE, User.Status.ACTIVE]
        POLICIES_CREATE = [User.PolicyRoles.CREATE, User.Status.ACTIVE]
        POLICIES_UPDATE = [User.PolicyRoles.UPDATE, User.Status.ACTIVE]
        POLICIES_USER = [User.PolicyRoles.USER, User.Status.ACTIVE]
        POLICIES_MULTIPLE = [User.PolicyRoles.UPDATE, User.PolicyRoles.DELETE, User.Status.ACTIVE]
        POLICIES_NO = []

        # Admin
        self.assertEqual(self._require_login(self.user_admin, POLICIES_ADMIN).status_code, 200)

        self.assertEqual(self._require_login(self.user_admin, POLICIES_DELETE).status_code, 200)

        self.assertEqual(self._require_login(self.user_admin, POLICIES_CREATE).status_code, 200)

        self.assertEqual(self._require_login(self.user_admin, POLICIES_UPDATE).status_code, 200)

        self.assertEqual(self._require_login(self.user_admin, POLICIES_USER).status_code, 200)

        self.assertEqual(self._require_login(self.user_admin, POLICIES_MULTIPLE).status_code, 200)

        self.assertEqual(self._require_login(self.user_admin, POLICIES_NO).status_code, 200)

        # Delete
        self.assertEqual(self._require_login(self.user_delete, POLICIES_ADMIN).status_code, 401)

        self.assertEqual(self._require_login(self.user_delete, POLICIES_DELETE).status_code, 200)

        self.assertEqual(self._require_login(self.user_delete, POLICIES_CREATE).status_code, 200)

        self.assertEqual(self._require_login(self.user_delete, POLICIES_UPDATE).status_code, 200)

        self.assertEqual(self._require_login(self.user_delete, POLICIES_USER).status_code, 200)

        self.assertEqual(self._require_login(self.user_delete, POLICIES_MULTIPLE).status_code, 200)

        self.assertEqual(self._require_login(self.user_delete, POLICIES_NO).status_code, 200)

        # Create
        self.assertEqual(self._require_login(self.user_create, POLICIES_ADMIN).status_code, 401)

        self.assertEqual(self._require_login(self.user_create, POLICIES_DELETE).status_code, 401)

        self.assertEqual(self._require_login(self.user_create, POLICIES_CREATE).status_code, 200)

        self.assertEqual(self._require_login(self.user_create, POLICIES_UPDATE).status_code, 200)

        self.assertEqual(self._require_login(self.user_create, POLICIES_USER).status_code, 200)

        self.assertEqual(self._require_login(self.user_create, POLICIES_MULTIPLE).status_code, 200)

        self.assertEqual(self._require_login(self.user_create, POLICIES_NO).status_code, 200)

        # Update
        self.assertEqual(self._require_login(self.user_update, POLICIES_ADMIN).status_code, 401)

        self.assertEqual(self._require_login(self.user_update, POLICIES_DELETE).status_code, 401)

        self.assertEqual(self._require_login(self.user_update, POLICIES_CREATE).status_code, 401)

        self.assertEqual(self._require_login(self.user_update, POLICIES_UPDATE).status_code, 200)

        self.assertEqual(self._require_login(self.user_update, POLICIES_USER).status_code, 200)

        self.assertEqual(self._require_login(self.user_update, POLICIES_MULTIPLE).status_code, 200)

        self.assertEqual(self._require_login(self.user_update, POLICIES_NO).status_code, 200)

        # User
        self.assertEqual(self._require_login(self.user_user, POLICIES_ADMIN).status_code, 401)

        self.assertEqual(self._require_login(self.user_user, POLICIES_DELETE).status_code, 401)

        self.assertEqual(self._require_login(self.user_user, POLICIES_CREATE).status_code, 401)

        self.assertEqual(self._require_login(self.user_user, POLICIES_UPDATE).status_code, 401)

        self.assertEqual(self._require_login(self.user_user, POLICIES_USER).status_code, 200)

        self.assertEqual(self._require_login(self.user_user, POLICIES_MULTIPLE).status_code, 401)

        self.assertEqual(self._require_login(self.user_user, POLICIES_NO).status_code, 200)

        # Banned users
        self.assertEqual(self._require_login(self.user_ban, POLICIES_ADMIN).status_code, 401)

        self.assertEqual(self._require_login(self.user_ban, POLICIES_DELETE).status_code, 401)

        self.assertEqual(self._require_login(self.user_ban, POLICIES_CREATE).status_code, 401)

        self.assertEqual(self._require_login(self.user_ban, POLICIES_UPDATE).status_code, 401)

        self.assertEqual(self._require_login(self.user_ban, POLICIES_USER).status_code, 401)

        self.assertEqual(self._require_login(self.user_ban, POLICIES_MULTIPLE).status_code, 401)

        self.assertEqual(self._require_login(self.user_ban, POLICIES_NO).status_code, 200)

        # Not active users
        self.assertEqual(self._require_login(self.user_inactive, POLICIES_ADMIN).status_code, 401)

        self.assertEqual(self._require_login(self.user_inactive, POLICIES_DELETE).status_code, 401)

        self.assertEqual(self._require_login(self.user_inactive, POLICIES_CREATE).status_code, 401)

        self.assertEqual(self._require_login(self.user_inactive, POLICIES_UPDATE).status_code, 401)

        self.assertEqual(self._require_login(self.user_inactive, POLICIES_USER).status_code, 401)

        self.assertEqual(self._require_login(self.user_inactive, POLICIES_MULTIPLE).status_code, 401)

        self.assertEqual(self._require_login(self.user_inactive, POLICIES_NO).status_code, 200)

    def _test_expiry(self):
        POLICIES_NO = []
        self.assertEqual(self._require_login(self.user_admin, POLICIES_NO).status_code, 200)

        with freeze_time(datetime.now() + timedelta(seconds=31)):
            with self.assertLogs() as cm:
                self.assertEqual(self._require_login(self.user_admin, POLICIES_NO).status_code, 401)
            self.assertIn('ExpiredSignatureError', str(cm.output))
            self.assertIn('handle_exception got ExpiredSignatureError error for function', str(cm.output))

    def _test_decorator_flask(self):
        view_calls.clear()
        self.assertEqual(self._require_login(self.user_delete, [], admin_entry_flask).status_code, 401)
        self.assertEqual([], view_calls)
        self.assertEqual(self._require_login(self.user_delete, [], delete_entry_flask).status_code, 200)
        self.assertEqual(['delete_entry_flask'], view_calls)

    def _test_decorator_django(self):
        view_calls.clear()
        self.assertEqual(self._require_login(self.user_delete, [], admin_entry_django).status_code, 401)
        self.assertEqual([], view_calls)
        self.assertEqual(self._require_login(self.user_delete, [], delete_entry_django).status_code, 200)
        self.assertEqual(['delete_entry_django'], view_calls)


@RequireLoginDjango(policies=[User.PolicyRoles.ADMIN, User.Status.ACTIVE])
def admin_entry_django(request):
    view_calls.append('admin_entry_django')
    return response_status(HTTPStatus.OK)


@RequireLoginDjango(policies=[User.PolicyRoles.DELETE, User.Status.ACTIVE])
def delete_entry_django(request):
    view_calls.append('delete_entry_django')
    return response_status(HTTPStatus.OK)


@RequireLoginFlask(policies=[User.PolicyRoles.ADMIN, User.Status.ACTIVE])
def admin_entry_flask():
    view_calls.append('admin_entry_flask')
    return response_status(HTTPStatus.OK)


@RequireLoginFlask(policies=[User.PolicyRoles.DELETE, User.Status.ACTIVE])
def delete_entry_flask():
    view_calls.append('delete_entry_flask')
    return response_status(HTTPStatus.OK)
