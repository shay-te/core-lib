import unittest
from datetime import timedelta, datetime
from typing import Callable

import jwt
from django.conf import settings
from django.http import HttpRequest
from flask import request, Flask
from flask_wtf.csrf import CSRFProtect
from freezegun import freeze_time
from werkzeug.http import dump_cookie
from core_lib.cache.cache_handler_ram import CacheHandlerRam
from core_lib.core_lib import CoreLib
from core_lib.data_transform.result_to_dict import result_to_dict
from core_lib.session.security_handler import SecurityHandler
from core_lib.web_helpers.django.require_login import RequireLogin as RequireLoginDjango
from core_lib.web_helpers.flask.require_login import RequireLogin as RequireLoginFlask
from core_lib.web_helpers.require_login_helper import require_login
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
from tests.test_data.test_user_security_utils import CustomerSecurity, user_data_access, User, has_access

# SECURITY HANDLER REGISTER
secret_key = 'super-secret'
cookie_name = 'my_cookie_name'
security_handler = CustomerSecurity(cookie_name, secret_key, timedelta(seconds=30))
SecurityHandler.register(security_handler)


class TestUserSecurity(unittest.TestCase):
    @classmethod
    def setUp(cls):
        CoreLib.cache_registry.unregister('test_user_security')

        cls.admin = result_to_dict(
            user_data_access.create({'username': 'admin', 'email': 'admin@def.com', 'role': User.PolicyRoles.ADMIN})
        )
        cls.delete = result_to_dict(
            user_data_access.create({'username': 'delete', 'email': 'delete@def.com', 'role': User.PolicyRoles.DELETE})
        )
        cls.create = result_to_dict(
            user_data_access.create({'username': 'create', 'email': 'create@def.com', 'role': User.PolicyRoles.CREATE})
        )
        cls.update = result_to_dict(
            user_data_access.create({'username': 'update', 'email': 'update@def.com', 'role': User.PolicyRoles.UPDATE})
        )
        cls.user = result_to_dict(
            user_data_access.create({'username': 'user', 'email': 'user@def.com', 'role': User.PolicyRoles.USER})
        )
        cls.user_ban = result_to_dict(
            user_data_access.create(
                {'username': 'user', 'email': 'user@def.com', 'role': User.PolicyRoles.USER, 'status': User.Status.BAN}
            )
        )
        cls.user_inactive = result_to_dict(
            user_data_access.create(
                {
                    'username': 'user',
                    'email': 'user@def.com',
                    'role': User.PolicyRoles.USER,
                    'status': User.Status.NOT_ACTIVE,
                }
            )
        )

        exp = datetime.now() + timedelta(seconds=30)
        cls.admin.update({'exp': exp})
        cls.delete.update({'exp': exp})
        cls.create.update({'exp': exp})
        cls.update.update({'exp': exp})
        cls.user.update({'exp': exp})
        cls.user_ban.update({'exp': exp})
        cls.user_inactive.update({'exp': exp})

        CoreLib.cache_registry.register('test_user_security', CacheHandlerRam())
        app = Flask(__name__)
        csrf = CSRFProtect()
        csrf.init_app(app)
        cls.app = app

    def test_has_access(self):
        self.assertTrue(
            has_access(security_handler.from_session_data(self.admin), [User.PolicyRoles.ADMIN, User.Status.ACTIVE])
        )
        self.assertTrue(has_access(security_handler.from_session_data(self.delete), [User.PolicyRoles.DELETE]))
        self.assertTrue(has_access(security_handler.from_session_data(self.create), [User.PolicyRoles.CREATE]))
        self.assertTrue(has_access(security_handler.from_session_data(self.update), [User.PolicyRoles.UPDATE]))
        self.assertTrue(has_access(security_handler.from_session_data(self.user), [User.PolicyRoles.USER]))

        self.assertFalse(has_access(security_handler.from_session_data(self.user), [User.PolicyRoles.ADMIN]))
        self.assertFalse(has_access(security_handler.from_session_data(self.update), [User.PolicyRoles.DELETE]))
        self.assertFalse(has_access(security_handler.from_session_data(self.user), [User.PolicyRoles.CREATE]))
        self.assertFalse(
            has_access(security_handler.from_session_data(self.admin), [User.PolicyRoles.ADMIN, User.Status.NOT_ACTIVE])
        )

        self.assertTrue(
            has_access(security_handler.from_session_data(self.delete), [User.PolicyRoles.UPDATE, User.Status.ACTIVE])
        )
        self.assertTrue(
            has_access(security_handler.from_session_data(self.update), [User.PolicyRoles.USER, User.Status.ACTIVE])
        )
        self.assertTrue(
            has_access(security_handler.from_session_data(self.admin), [User.PolicyRoles.CREATE, User.Status.ACTIVE])
        )
        self.assertTrue(
            has_access(security_handler.from_session_data(self.create), [User.PolicyRoles.UPDATE, User.Status.ACTIVE])
        )
        self.assertTrue(
            has_access(security_handler.from_session_data(self.delete), [User.PolicyRoles.CREATE, User.Status.ACTIVE])
        )

        self.assertTrue(has_access(security_handler.from_session_data(self.admin), [User.Status.ACTIVE]))
        self.assertTrue(has_access(security_handler.from_session_data(self.delete), [User.Status.ACTIVE]))
        self.assertTrue(has_access(security_handler.from_session_data(self.create), [User.Status.ACTIVE]))
        self.assertTrue(has_access(security_handler.from_session_data(self.update), [User.Status.ACTIVE]))
        self.assertTrue(has_access(security_handler.from_session_data(self.user), [User.Status.ACTIVE]))

    def test_session_data(self):
        time_stamp = datetime.utcnow().timestamp()
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
        if not settings.configured:
            settings.configure()
            settings.DEFAULT_CHARSET = 'utf-8'
        WebHelpersUtils.init(WebHelpersUtils.ServerType.DJANGO)

        self._test_secure_entry()
        self._test_expiry()

    def test_secure_flask(self):
        # FLASK INIT
        WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)

        self._test_secure_entry()
        self._test_expiry()

    def _create_and_send_request(self, payload: dict, policies: list):
        token = jwt.encode(payload, secret_key)
        if WebHelpersUtils.get_server_type() == WebHelpersUtils.ServerType.FLASK:
            header = dump_cookie(cookie_name, token)
            with self.app.test_request_context(environ_base={'HTTP_COOKIE': header}):
                self.assertEqual(request.cookies[cookie_name], token)
                return require_login(request, policies, entry_as_per_policies)
        else:
            request_object = HttpRequest
            request_object.COOKIES = {cookie_name: token}
            self.assertEqual(request_object.COOKIES[cookie_name], token)
            return require_login(request_object, policies, entry_as_per_policies)

    def _test_secure_entry(self):

        POLICIES_ADMIN = [User.PolicyRoles.ADMIN, User.Status.ACTIVE]
        POLICIES_DELETE = [User.PolicyRoles.DELETE, User.Status.ACTIVE]
        POLICIES_CREATE = [User.PolicyRoles.CREATE, User.Status.ACTIVE]
        POLICIES_UPDATE = [User.PolicyRoles.UPDATE, User.Status.ACTIVE]
        POLICIES_USER = [User.PolicyRoles.USER, User.Status.ACTIVE]
        POLICIES_MULTIPLE = [User.PolicyRoles.UPDATE, User.PolicyRoles.DELETE, User.Status.ACTIVE]
        POLICIES_NO = []

        # Admin
        self.assertEqual(self._create_and_send_request(self.admin, POLICIES_ADMIN).status_code, 200)

        self.assertEqual(self._create_and_send_request(self.admin, POLICIES_DELETE).status_code, 200)

        self.assertEqual(self._create_and_send_request(self.admin, POLICIES_CREATE).status_code, 200)

        self.assertEqual(self._create_and_send_request(self.admin, POLICIES_UPDATE).status_code, 200)

        self.assertEqual(self._create_and_send_request(self.admin, POLICIES_USER).status_code, 200)

        self.assertEqual(self._create_and_send_request(self.admin, POLICIES_MULTIPLE).status_code, 200)

        self.assertEqual(self._create_and_send_request(self.admin, POLICIES_NO).status_code, 200)

        # Delete
        self.assertEqual(self._create_and_send_request(self.delete, POLICIES_ADMIN).status_code, 401)

        self.assertEqual(self._create_and_send_request(self.delete, POLICIES_DELETE).status_code, 200)

        self.assertEqual(self._create_and_send_request(self.delete, POLICIES_CREATE).status_code, 200)

        self.assertEqual(self._create_and_send_request(self.delete, POLICIES_UPDATE).status_code, 200)

        self.assertEqual(self._create_and_send_request(self.delete, POLICIES_USER).status_code, 200)

        self.assertEqual(self._create_and_send_request(self.delete, POLICIES_MULTIPLE).status_code, 200)

        self.assertEqual(self._create_and_send_request(self.delete, POLICIES_NO).status_code, 200)

        # Create
        self.assertEqual(self._create_and_send_request(self.create, POLICIES_ADMIN).status_code, 401)

        self.assertEqual(self._create_and_send_request(self.create, POLICIES_DELETE).status_code, 401)

        self.assertEqual(self._create_and_send_request(self.create, POLICIES_CREATE).status_code, 200)

        self.assertEqual(self._create_and_send_request(self.create, POLICIES_UPDATE).status_code, 200)

        self.assertEqual(self._create_and_send_request(self.create, POLICIES_USER).status_code, 200)

        self.assertEqual(self._create_and_send_request(self.create, POLICIES_MULTIPLE).status_code, 200)

        self.assertEqual(self._create_and_send_request(self.create, POLICIES_NO).status_code, 200)

        # Update
        self.assertEqual(self._create_and_send_request(self.update, POLICIES_ADMIN).status_code, 401)

        self.assertEqual(self._create_and_send_request(self.update, POLICIES_DELETE).status_code, 401)

        self.assertEqual(self._create_and_send_request(self.update, POLICIES_CREATE).status_code, 401)

        self.assertEqual(self._create_and_send_request(self.update, POLICIES_UPDATE).status_code, 200)

        self.assertEqual(self._create_and_send_request(self.update, POLICIES_USER).status_code, 200)

        self.assertEqual(self._create_and_send_request(self.update, POLICIES_MULTIPLE).status_code, 200)

        self.assertEqual(self._create_and_send_request(self.update, POLICIES_NO).status_code, 200)

        # User
        self.assertEqual(self._create_and_send_request(self.user, POLICIES_ADMIN).status_code, 401)

        self.assertEqual(self._create_and_send_request(self.user, POLICIES_DELETE).status_code, 401)

        self.assertEqual(self._create_and_send_request(self.user, POLICIES_CREATE).status_code, 401)

        self.assertEqual(self._create_and_send_request(self.user, POLICIES_UPDATE).status_code, 401)

        self.assertEqual(self._create_and_send_request(self.user, POLICIES_USER).status_code, 200)

        self.assertEqual(self._create_and_send_request(self.user, POLICIES_MULTIPLE).status_code, 401)

        self.assertEqual(self._create_and_send_request(self.user, POLICIES_NO).status_code, 200)

        # Banned users
        self.assertEqual(self._create_and_send_request(self.user_ban, POLICIES_ADMIN).status_code, 401)

        self.assertEqual(self._create_and_send_request(self.user_ban, POLICIES_DELETE).status_code, 401)

        self.assertEqual(self._create_and_send_request(self.user_ban, POLICIES_CREATE).status_code, 401)

        self.assertEqual(self._create_and_send_request(self.user_ban, POLICIES_UPDATE).status_code, 401)

        self.assertEqual(self._create_and_send_request(self.user_ban, POLICIES_USER).status_code, 401)

        self.assertEqual(self._create_and_send_request(self.user_ban, POLICIES_MULTIPLE).status_code, 401)

        self.assertEqual(self._create_and_send_request(self.user_ban, POLICIES_NO).status_code, 200)

        # Not active users
        self.assertEqual(self._create_and_send_request(self.user_inactive, POLICIES_ADMIN).status_code, 401)

        self.assertEqual(self._create_and_send_request(self.user_inactive, POLICIES_DELETE).status_code, 401)

        self.assertEqual(self._create_and_send_request(self.user_inactive, POLICIES_CREATE).status_code, 401)

        self.assertEqual(self._create_and_send_request(self.user_inactive, POLICIES_UPDATE).status_code, 401)

        self.assertEqual(self._create_and_send_request(self.user_inactive, POLICIES_USER).status_code, 401)

        self.assertEqual(self._create_and_send_request(self.user_inactive, POLICIES_MULTIPLE).status_code, 401)

        self.assertEqual(self._create_and_send_request(self.user_inactive, POLICIES_NO).status_code, 200)

    def _test_expiry(self):
        POLICIES_NO = []
        self.assertEqual(self._create_and_send_request(self.admin, POLICIES_NO).status_code, 200)

        with freeze_time(datetime.now() + timedelta(seconds=31)):
            with self.assertLogs() as cm:
                self.assertEqual(self._create_and_send_request(self.admin, POLICIES_NO).status_code, 401)
            self.assertIn('ExpiredSignatureError', str(cm.output))
            self.assertIn('handle_exception got error for function', str(cm.output))


def entry_as_per_policies():
    """
    Skipped because this a testing function and returns nothing
    """
    pass
