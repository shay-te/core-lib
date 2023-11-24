import unittest
from datetime import timedelta, datetime
from typing import Callable

import jwt
from django.conf import settings
from django.http import HttpRequest
from flask import request as flask_request, Flask
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
                return require_login(flask_request, policies, lambda: True)
        else:
            django_request = HttpRequest
            django_request.COOKIES = {cookie_name: token}
            self.assertEqual(django_request.COOKIES[cookie_name], token)
            if decorated_function:
                return decorated_function(django_request)
            return require_login(django_request, policies, lambda: True)

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
        self.assertEqual(self._require_login(self.user_delete, [], admin_entry_flask).status_code, 401)
        self.assertEqual(self._require_login(self.user_delete, [], delete_entry_flask).status_code, 200)

    def _test_decorator_django(self):
        self.assertEqual(self._require_login(self.user_delete, [], admin_entry_django).status_code, 401)
        self.assertEqual(self._require_login(self.user_delete, [], delete_entry_django).status_code, 200)


@RequireLoginDjango(policies=[User.PolicyRoles.ADMIN, User.Status.ACTIVE])
def admin_entry_django(request):
    """
    Skipped because this a testing function and returns nothing
    """
    pass


@RequireLoginDjango(policies=[User.PolicyRoles.DELETE, User.Status.ACTIVE])
def delete_entry_django(request):
    """
    Skipped because this a testing function and returns nothing
    """
    pass


@RequireLoginFlask(policies=[User.PolicyRoles.ADMIN, User.Status.ACTIVE])
def admin_entry_flask():
    """
    Skipped because this a testing function and returns nothing
    """
    pass


@RequireLoginFlask(policies=[User.PolicyRoles.DELETE, User.Status.ACTIVE])
def delete_entry_flask():
    """
    Skipped because this a testing function and returns nothing
    """
    pass
