from datetime import datetime, timedelta
from unittest import TestCase
import jwt
from django.conf import settings
from django.http import HttpRequest
from freezegun import freeze_time

from core_lib.cache.cache_handler_ram import CacheHandlerRam
from core_lib.core_lib import CoreLib
from core_lib.data_transform.result_to_dict import result_to_dict
from core_lib.session.security_handler import SecurityHandler
from core_lib.web_helpers.django.require_login import RequireLogin
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
from tests.test_data.test_user_security_utils import User, user_data_access, CustomerSecurity

secret_key = 'super-secret'
cookie_name = 'my_cookie_name'
security_handler = CustomerSecurity(cookie_name, secret_key, timedelta(seconds=30))
SecurityHandler.register(security_handler)

# DJANGO INIT
if not settings.configured:
    settings.configure()
    settings.DEFAULT_CHARSET = 'utf-8'
web_util = WebHelpersUtils()
web_util.init(web_util.ServerType.DJANGO)


class TestRequireLoginDjango(TestCase):
    @classmethod
    def setUp(cls):
        CoreLib.cache_registry.unregister('test_require_login_django')

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

        CoreLib.cache_registry.register('test_require_login_django', CacheHandlerRam())

    def _create_request(self, payload: dict):
        request_object = HttpRequest
        token = jwt.encode(payload, secret_key)
        request_object.COOKIES = {cookie_name: token}
        return request_object

    def test_secure_entry_django(self):
        # Admin
        response = admin_entry(self._create_request(self.admin))
        self.assertEqual(response.status_code, 200)

        response = delete_entry(self._create_request(self.admin))
        self.assertEqual(response.status_code, 200)

        response = create_entry(self._create_request(self.admin))
        self.assertEqual(response.status_code, 200)

        response = update_entry(self._create_request(self.admin))
        self.assertEqual(response.status_code, 200)

        response = user_entry(self._create_request(self.admin))
        self.assertEqual(response.status_code, 200)

        response = multiple_entry(self._create_request(self.admin))
        self.assertEqual(response.status_code, 200)

        response = no_policy_entry(self._create_request(self.admin))
        self.assertEqual(response.status_code, 200)

        # Delete
        response = admin_entry(self._create_request(self.delete))
        self.assertEqual(response.status_code, 401)

        response = delete_entry(self._create_request(self.delete))
        self.assertEqual(response.status_code, 200)

        response = create_entry(self._create_request(self.delete))
        self.assertEqual(response.status_code, 200)

        response = update_entry(self._create_request(self.delete))
        self.assertEqual(response.status_code, 200)

        response = user_entry(self._create_request(self.delete))
        self.assertEqual(response.status_code, 200)

        response = multiple_entry(self._create_request(self.delete))
        self.assertEqual(response.status_code, 200)

        response = no_policy_entry(self._create_request(self.delete))
        self.assertEqual(response.status_code, 200)

        # Create
        response = admin_entry(self._create_request(self.create))
        self.assertEqual(response.status_code, 401)

        response = delete_entry(self._create_request(self.create))
        self.assertEqual(response.status_code, 401)

        response = create_entry(self._create_request(self.create))
        self.assertEqual(response.status_code, 200)

        response = update_entry(self._create_request(self.create))
        self.assertEqual(response.status_code, 200)

        response = user_entry(self._create_request(self.create))
        self.assertEqual(response.status_code, 200)

        response = multiple_entry(self._create_request(self.create))
        self.assertEqual(response.status_code, 200)

        response = no_policy_entry(self._create_request(self.create))
        self.assertEqual(response.status_code, 200)

        # Update
        response = admin_entry(self._create_request(self.update))
        self.assertEqual(response.status_code, 401)

        response = delete_entry(self._create_request(self.update))
        self.assertEqual(response.status_code, 401)

        response = create_entry(self._create_request(self.update))
        self.assertEqual(response.status_code, 401)

        response = update_entry(self._create_request(self.update))
        self.assertEqual(response.status_code, 200)

        response = user_entry(self._create_request(self.update))
        self.assertEqual(response.status_code, 200)

        response = multiple_entry(self._create_request(self.update))
        self.assertEqual(response.status_code, 200)

        response = no_policy_entry(self._create_request(self.update))
        self.assertEqual(response.status_code, 200)

        # User
        response = admin_entry(self._create_request(self.user))
        self.assertEqual(response.status_code, 401)

        response = delete_entry(self._create_request(self.user))
        self.assertEqual(response.status_code, 401)

        response = create_entry(self._create_request(self.user))
        self.assertEqual(response.status_code, 401)

        response = update_entry(self._create_request(self.user))
        self.assertEqual(response.status_code, 401)

        response = user_entry(self._create_request(self.user))
        self.assertEqual(response.status_code, 200)

        response = multiple_entry(self._create_request(self.user))
        self.assertEqual(response.status_code, 401)

        response = no_policy_entry(self._create_request(self.user))
        self.assertEqual(response.status_code, 200)

        # Banned users
        response = admin_entry(self._create_request(self.user_ban))
        self.assertEqual(response.status_code, 401)

        response = delete_entry(self._create_request(self.user_ban))
        self.assertEqual(response.status_code, 401)

        response = create_entry(self._create_request(self.user_ban))
        self.assertEqual(response.status_code, 401)

        response = update_entry(self._create_request(self.user_ban))
        self.assertEqual(response.status_code, 401)

        response = user_entry(self._create_request(self.user_ban))
        self.assertEqual(response.status_code, 401)

        response = multiple_entry(self._create_request(self.user_ban))
        self.assertEqual(response.status_code, 401)

        response = no_policy_entry(self._create_request(self.user_ban))
        self.assertEqual(response.status_code, 200)

        # Not active users
        response = admin_entry(self._create_request(self.user_inactive))
        self.assertEqual(response.status_code, 401)

        response = delete_entry(self._create_request(self.user_inactive))
        self.assertEqual(response.status_code, 401)

        response = create_entry(self._create_request(self.user_inactive))
        self.assertEqual(response.status_code, 401)

        response = update_entry(self._create_request(self.user_inactive))
        self.assertEqual(response.status_code, 401)

        response = user_entry(self._create_request(self.user_inactive))
        self.assertEqual(response.status_code, 401)

        response = multiple_entry(self._create_request(self.user_inactive))
        self.assertEqual(response.status_code, 401)

        response = no_policy_entry(self._create_request(self.user_inactive))
        self.assertEqual(response.status_code, 200)

    def test_expiry(self):
        request = self._create_request(self.admin)

        response = no_policy_entry(request)
        self.assertEqual(response.status_code, 200)

        with freeze_time(datetime.now() + timedelta(seconds=31)):
            with self.assertLogs() as cm:
                resp_json = no_policy_entry(request)
                self.assertEqual(resp_json.status_code, 401)
            self.assertIn('ExpiredSignatureError', str(cm.output))
            self.assertIn('handle_exception got error for function', str(cm.output))


@RequireLogin(policies=[User.PolicyRoles.ADMIN, User.Status.ACTIVE])
def admin_entry(request):
    pass


@RequireLogin(policies=[User.PolicyRoles.DELETE, User.Status.ACTIVE])
def delete_entry(request):
    pass


@RequireLogin(policies=[User.PolicyRoles.CREATE, User.Status.ACTIVE])
def create_entry(request):
    pass


@RequireLogin(policies=[User.PolicyRoles.UPDATE, User.Status.ACTIVE])
def update_entry(request):
    pass


@RequireLogin(policies=[User.PolicyRoles.USER, User.Status.ACTIVE])
def user_entry(request):
    pass


@RequireLogin(policies=[User.PolicyRoles.UPDATE, User.PolicyRoles.DELETE, User.Status.ACTIVE])
def multiple_entry(request):
    pass


@RequireLogin(policies=[])
def no_policy_entry(request):
    pass
