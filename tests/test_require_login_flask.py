from datetime import datetime, timedelta
from typing import Callable, Any
from unittest import TestCase
import jwt
from freezegun import freeze_time
from flask import request
from werkzeug.http import dump_cookie
from core_lib.cache.cache_handler_ram import CacheHandlerRam
from core_lib.core_lib import CoreLib
from core_lib.data_transform.result_to_dict import result_to_dict
from core_lib.session.security_handler import SecurityHandler
from core_lib.web_helpers.flask.require_login import RequireLogin
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
from tests.test_data.test_user_security_utils import User, user_data_access, CustomerSecurity
from flask import Flask

secret_key = 'super-secret'
cookie_name = 'my_cookie_name'
security_handler = CustomerSecurity(cookie_name, secret_key, timedelta(seconds=30))
SecurityHandler.register(security_handler)

# FLASK INIT
web_util = WebHelpersUtils()
web_util.init(web_util.ServerType.FLASK)


class TestRequireLoginFlask(TestCase):
    @classmethod
    def setUp(cls):
        CoreLib.cache_registry.unregister('test_require_login_flask')

        cls.admin = result_to_dict(
            user_data_access.create({'username': 'admin', 'email': 'admin@def.com', 'role': User.PolicyRoles.ADMIN}))
        cls.delete = result_to_dict(
            user_data_access.create({'username': 'delete', 'email': 'delete@def.com', 'role': User.PolicyRoles.DELETE}))
        cls.create = result_to_dict(
            user_data_access.create({'username': 'create', 'email': 'create@def.com', 'role': User.PolicyRoles.CREATE}))
        cls.update = result_to_dict(
            user_data_access.create({'username': 'update', 'email': 'update@def.com', 'role': User.PolicyRoles.UPDATE}))
        cls.user = result_to_dict(
            user_data_access.create({'username': 'user', 'email': 'user@def.com', 'role': User.PolicyRoles.USER}))
        cls.user_ban = result_to_dict(user_data_access.create(
            {'username': 'user', 'email': 'user@def.com', 'role': User.PolicyRoles.USER, 'status': User.Status.BAN}))
        cls.user_inactive = result_to_dict(user_data_access.create(
            {'username': 'user', 'email': 'user@def.com', 'role': User.PolicyRoles.USER,
                'status': User.Status.NOT_ACTIVE, }))

        exp = datetime.now() + timedelta(seconds=30)
        cls.admin.update({'exp': exp})
        cls.delete.update({'exp': exp})
        cls.create.update({'exp': exp})
        cls.update.update({'exp': exp})
        cls.user.update({'exp': exp})
        cls.user_ban.update({'exp': exp})
        cls.user_inactive.update({'exp': exp})

        CoreLib.cache_registry.register('test_require_login_flask', CacheHandlerRam())
        cls.app = Flask(__name__)

    def _create_and_send_request(self, payload: dict, func: Callable[[], Any]):
        token = jwt.encode(payload, secret_key)
        header = dump_cookie(cookie_name, token)
        with self.app.test_request_context(environ_base={'HTTP_COOKIE': header}):
            assert request.cookies[cookie_name] == token
            return func()

    def test_secure_entry_flask(self):
        # Admin
        response = self._create_and_send_request(self.admin, admin_entry)
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.admin, delete_entry)
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.admin, create_entry)
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.admin, update_entry)
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.admin, user_entry)
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.admin,  multiple_entry)
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.admin, no_policy_entry)
        self.assertEqual(response.status_code, 200)

        # Delete
        response = self._create_and_send_request(self.delete, admin_entry)
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.delete, delete_entry)
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.delete, create_entry)
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.delete, update_entry)
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.delete, user_entry)
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.delete, multiple_entry)
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.delete, no_policy_entry)
        self.assertEqual(response.status_code, 200)

        # Create
        response = self._create_and_send_request(self.create, admin_entry)
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.create, delete_entry)
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.create, create_entry)
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.create, update_entry)
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.create, user_entry)
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.create, multiple_entry)
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.create, no_policy_entry)
        self.assertEqual(response.status_code, 200)

        # Update
        response = self._create_and_send_request(self.update, admin_entry)
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.update, delete_entry)
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.update, create_entry)
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.update, update_entry)
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.update, user_entry)
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.update, multiple_entry)
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.update, no_policy_entry)
        self.assertEqual(response.status_code, 200)

        # User
        response = self._create_and_send_request(self.user, admin_entry)
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user, delete_entry)
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user, create_entry)
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user, update_entry)
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user, user_entry)
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.user, multiple_entry)
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user, no_policy_entry)
        self.assertEqual(response.status_code, 200)

        # Banned users
        response = self._create_and_send_request(self.user_ban, admin_entry)
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user_ban, delete_entry)
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user_ban, create_entry)
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user_ban, update_entry)
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user_ban, user_entry)
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user_ban, multiple_entry)
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user_ban, no_policy_entry)
        self.assertEqual(response.status_code, 200)

        # Not active users
        response = self._create_and_send_request(self.user_inactive, admin_entry)
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user_inactive, delete_entry)
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user_inactive, create_entry)
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user_inactive, update_entry)
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user_inactive, user_entry)
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user_inactive, multiple_entry)
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user_inactive, no_policy_entry)
        self.assertEqual(response.status_code, 200)

    def test_expiry(self):
        response = self._create_and_send_request(self.admin, no_policy_entry)
        self.assertEqual(response.status_code, 200)

        with freeze_time(datetime.now() + timedelta(seconds=31)):
            with self.assertLogs() as cm:
                resp_json = self._create_and_send_request(self.admin, no_policy_entry)
                self.assertEqual(resp_json.status_code, 401)
            self.assertIn('ExpiredSignatureError', str(cm.output))
            self.assertIn('handle_exception got error for function', str(cm.output))


@RequireLogin(policies=[User.PolicyRoles.ADMIN, User.Status.ACTIVE])
def admin_entry():
    pass


@RequireLogin(policies=[User.PolicyRoles.DELETE, User.Status.ACTIVE])
def delete_entry():
    pass


@RequireLogin(policies=[User.PolicyRoles.CREATE, User.Status.ACTIVE])
def create_entry():
    pass


@RequireLogin(policies=[User.PolicyRoles.UPDATE, User.Status.ACTIVE])
def update_entry():
    pass


@RequireLogin(policies=[User.PolicyRoles.USER, User.Status.ACTIVE])
def user_entry():
    pass


@RequireLogin(policies=[User.PolicyRoles.UPDATE, User.PolicyRoles.DELETE, User.Status.ACTIVE])
def multiple_entry():
    pass


@RequireLogin(policies=[])
def no_policy_entry():
    pass
