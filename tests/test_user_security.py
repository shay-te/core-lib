import unittest
from datetime import timedelta, datetime
import jwt
from django.conf import settings
from django.http import HttpRequest
from flask import request, Flask
from freezegun import freeze_time
from werkzeug.http import dump_cookie
from core_lib.cache.cache_handler_ram import CacheHandlerRam
from core_lib.core_lib import CoreLib
from core_lib.data_transform.result_to_dict import result_to_dict
from core_lib.session.security_handler import SecurityHandler
from core_lib.web_helpers.django.require_login import RequireLogin as RequireLoginDjango
from core_lib.web_helpers.flask.require_login import RequireLogin as RequireLoginFlask
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
        cls.app = Flask(__name__)
        cls.app.config['WTF_CSRF_ENABLED'] = True

        cls.map_function = {
            'flask': {
                'admin_entry': admin_entry_flask,
                'delete_entry': delete_entry_flask,
                'update_entry': update_entry_flask,
                'multiple_entry': multiple_entry_flask,
                'create_entry': create_entry_flask,
                'no_policy_entry': no_policy_entry_flask,
                'user_entry': user_entry_flask
            },
            'django': {
                'admin_entry': admin_entry_django,
                'delete_entry': delete_entry_django,
                'update_entry': update_entry_django,
                'multiple_entry': multiple_entry_django,
                'create_entry': create_entry_django,
                'no_policy_entry': no_policy_entry_django,
                'user_entry': user_entry_django
            }
        }

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

    def _create_and_send_request(self, payload: dict, func_type: str):
        token = jwt.encode(payload, secret_key)
        if WebHelpersUtils.get_server_type() == WebHelpersUtils.ServerType.FLASK:
            header = dump_cookie(cookie_name, token)
            with self.app.test_request_context(environ_base={'HTTP_COOKIE': header}):
                assert request.cookies[cookie_name] == token
                return self.map_function[WebHelpersUtils.ServerType.FLASK.value][func_type]()
        else:
            request_object = HttpRequest
            request_object.COOKIES = {cookie_name: token}
            return self.map_function[WebHelpersUtils.ServerType.DJANGO.value][func_type](request_object)

    def _test_secure_entry(self):
        # Admin
        response = self._create_and_send_request(self.admin, 'admin_entry')
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.admin, 'delete_entry')
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.admin, 'create_entry')
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.admin, 'update_entry')
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.admin, 'user_entry')
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.admin, 'multiple_entry')
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.admin, 'no_policy_entry')
        self.assertEqual(response.status_code, 200)

        # Delete
        response = self._create_and_send_request(self.delete, 'admin_entry')
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.delete, 'delete_entry')
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.delete, 'create_entry')
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.delete, 'update_entry')
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.delete, 'user_entry')
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.delete, 'multiple_entry')
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.delete, 'no_policy_entry')
        self.assertEqual(response.status_code, 200)

        # Create
        response = self._create_and_send_request(self.create, 'admin_entry')
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.create, 'delete_entry')
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.create, 'create_entry')
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.create, 'update_entry')
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.create, 'user_entry')
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.create, 'multiple_entry')
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.create, 'no_policy_entry')
        self.assertEqual(response.status_code, 200)

        # Update
        response = self._create_and_send_request(self.update, 'admin_entry')
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.update, 'delete_entry')
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.update, 'create_entry')
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.update, 'update_entry')
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.update, 'user_entry')
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.update, 'multiple_entry')
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.update, 'no_policy_entry')
        self.assertEqual(response.status_code, 200)

        # User
        response = self._create_and_send_request(self.user, 'admin_entry')
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user, 'delete_entry')
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user, 'create_entry')
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user, 'update_entry')
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user, 'user_entry')
        self.assertEqual(response.status_code, 200)

        response = self._create_and_send_request(self.user, 'multiple_entry')
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user, 'no_policy_entry')
        self.assertEqual(response.status_code, 200)

        # Banned users
        response = self._create_and_send_request(self.user_ban, 'admin_entry')
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user_ban, 'delete_entry')
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user_ban, 'create_entry')
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user_ban, 'update_entry')
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user_ban, 'user_entry')
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user_ban, 'multiple_entry')
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user_ban, 'no_policy_entry')
        self.assertEqual(response.status_code, 200)

        # Not active users
        response = self._create_and_send_request(self.user_inactive, 'admin_entry')
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user_inactive, 'delete_entry')
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user_inactive, 'create_entry')
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user_inactive, 'update_entry')
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user_inactive, 'user_entry')
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user_inactive, 'multiple_entry')
        self.assertEqual(response.status_code, 401)

        response = self._create_and_send_request(self.user_inactive, 'no_policy_entry')
        self.assertEqual(response.status_code, 200)

    def _test_expiry(self):
        response = self._create_and_send_request(self.admin, 'no_policy_entry')
        self.assertEqual(response.status_code, 200)

        with freeze_time(datetime.now() + timedelta(seconds=31)):
            with self.assertLogs() as cm:
                resp_json = self._create_and_send_request(self.admin, 'no_policy_entry')
                self.assertEqual(resp_json.status_code, 401)
            self.assertIn('ExpiredSignatureError', str(cm.output))
            self.assertIn('handle_exception got error for function', str(cm.output))


@RequireLoginDjango(policies=[User.PolicyRoles.ADMIN, User.Status.ACTIVE])
def admin_entry_django(request):
    """
    Skipped because this is a testing function and returns nothing
    """
    pass


@RequireLoginDjango(policies=[User.PolicyRoles.DELETE, User.Status.ACTIVE])
def delete_entry_django(request):
    """
    Skipped because this is a testing function and returns nothing
    """
    pass


@RequireLoginDjango(policies=[User.PolicyRoles.CREATE, User.Status.ACTIVE])
def create_entry_django(request):
    """
    Skipped because this is a testing function and returns nothing
    """
    pass


@RequireLoginDjango(policies=[User.PolicyRoles.UPDATE, User.Status.ACTIVE])
def update_entry_django(request):
    """
    Skipped because this is a testing function and returns nothing
    """
    pass


@RequireLoginDjango(policies=[User.PolicyRoles.USER, User.Status.ACTIVE])
def user_entry_django(request):
    """
    Skipped because this is a testing function and returns nothing
    """
    pass


@RequireLoginDjango(policies=[User.PolicyRoles.UPDATE, User.PolicyRoles.DELETE, User.Status.ACTIVE])
def multiple_entry_django(request):
    """
    Skipped because this is a testing function and returns nothing
    """
    pass


@RequireLoginDjango(policies=[])
def no_policy_entry_django(request):
    """
    Skipped because this is a testing function and returns nothing
    """
    pass


@RequireLoginFlask(policies=[User.PolicyRoles.ADMIN, User.Status.ACTIVE])
def admin_entry_flask():
    """
    Skipped because this is a testing function and returns nothing
    """
    pass


@RequireLoginFlask(policies=[User.PolicyRoles.DELETE, User.Status.ACTIVE])
def delete_entry_flask():
    """
    Skipped because this is a testing function and returns nothing
    """
    pass


@RequireLoginFlask(policies=[User.PolicyRoles.CREATE, User.Status.ACTIVE])
def create_entry_flask():
    """
    Skipped because this is a testing function and returns nothing
    """
    pass


@RequireLoginFlask(policies=[User.PolicyRoles.UPDATE, User.Status.ACTIVE])
def update_entry_flask():
    """
    Skipped because this is a testing function and returns nothing
    """
    pass


@RequireLoginFlask(policies=[User.PolicyRoles.USER, User.Status.ACTIVE])
def user_entry_flask():
    """
    Skipped because this is a testing function and returns nothing
    """
    pass


@RequireLoginFlask(policies=[User.PolicyRoles.UPDATE, User.PolicyRoles.DELETE, User.Status.ACTIVE])
def multiple_entry_flask():
    """
    Skipped because this is a testing function and returns nothing
    """
    pass


@RequireLoginFlask(policies=[])
def no_policy_entry_flask():
    """
    Skipped because this is a testing function and returns nothing
    """
    pass
