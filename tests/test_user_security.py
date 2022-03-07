import enum
import unittest
from datetime import timedelta, datetime
from http import HTTPStatus

import jwt
from django.conf import settings
from django.http import HttpRequest
from freezegun import freeze_time
from jwt import ExpiredSignatureError
from sqlalchemy import Integer, Column, VARCHAR

from core_lib.cache.cache_decorator import Cache
from core_lib.cache.cache_handler_ram import CacheHandlerRam
from core_lib.core_lib import CoreLib
from core_lib.data_layers.data.db.sqlalchemy.base import Base
from core_lib.data_layers.data.db.sqlalchemy.types.int_enum import IntEnum
from core_lib.data_layers.data_access.db.crud.crud import CRUD
from core_lib.data_layers.data_access.db.crud.crud_data_access import CRUDDataAccess
from core_lib.data_transform.result_to_dict import result_to_dict
from core_lib.rule_validator.rule_validator import ValueRuleValidator, RuleValidator
from core_lib.session.jwt_token_handler import JWTTokenHandler
from core_lib.session.security_handler import SecurityHandler
from core_lib.session.user_security import UserSecurity
from core_lib.web_helpers.decorators import handle_exceptions
from core_lib.web_helpers.django.decorators import RequireLogin
from core_lib.web_helpers.django.user_auth_middleware import UserAuthMiddleware
from core_lib.web_helpers.request_response_helpers import response_status
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
from tests.test_data.test_utils import connect_to_mem_db


# CRUD SETUP
class User(Base):
    __tablename__ = 'user_security'

    class PolicyRoles(enum.Enum):
        ADMIN = 1
        DELETE = 2
        CREATE = 3
        UPDATE = 4
        USER = 5

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(VARCHAR(length=255), nullable=False, default="")
    email = Column(VARCHAR(length=255), nullable=False, default="")
    role = Column('role', IntEnum(PolicyRoles), default=PolicyRoles.USER)


class UserDataAccess(CRUDDataAccess):
    allowed_update_types = [
        ValueRuleValidator('username', str),
        ValueRuleValidator('email', str),
    ]

    rules_validator = RuleValidator(allowed_update_types)

    def __init__(self):
        CRUD.__init__(self, User, connect_to_mem_db(), UserDataAccess.rules_validator)


# CRUD INIT
user_data_access = UserDataAccess()


@Cache(key='user_data_{u_id}', expire=timedelta(seconds=30))
def get_user(u_id):
    return result_to_dict(user_data_access.get(u_id))


# USER SECURITY SETUP
class SessionUser(object):
    def __init__(self, id: int, email: str, expiry: datetime):
        self.id = id
        self.email = email
        self.exp = expiry

    def __dict__(self):
        return {'id': self.id, 'email': self.email, 'exp': self.exp}


def has_access(user_policy, check_policies):
    if user_policy <= max(check_policies) or user_policy in check_policies:
        return True
    else:
        return False


class CustomerSecurity(UserSecurity):
    def __init__(self, cookie_name: str, secret: str, expiration_time: timedelta):
        UserSecurity.__init__(self, cookie_name, JWTTokenHandler(secret, expiration_time))

    def secure_entry(self, request, session_obj: SessionUser, policies: list):
        data_dict = get_user(session_obj.id)
        if data_dict['email'] == session_obj.email:
            if not policies:
                return response_status(HTTPStatus.OK)
            elif has_access(data_dict['role'], policies):
                return response_status(HTTPStatus.OK)
            else:
                return response_status(HTTPStatus.UNAUTHORIZED)
        else:
            return response_status(HTTPStatus.FORBIDDEN)

    def from_session_data(self, session_data: dict) -> SessionUser:
        return SessionUser(session_data['id'], session_data['email'], session_data['exp'])

    def generate_session_data(self, user) -> dict:
        return {
            'id': user['id'],
            'email': user['email'],
        }


# SECURITY HANDLER REGISTER
key = 'super-secret'
security_handler = CustomerSecurity('user_cookie', key, timedelta(seconds=30))
SecurityHandler.register(security_handler)

# DJANGO INIT
if not settings.configured:
    settings.configure()
    settings.DEFAULT_CHARSET = 'utf-8'

web_util = WebHelpersUtils()
web_util.init(web_util.ServerType.DJANGO)


class TestUserSecurity(unittest.TestCase):
    # admin = {'id': 1, 'email': 'admin@def.com', 'exp': datetime.now() + timedelta(seconds=30)}
    # delete = {'id': 2, 'email': 'delete@def.com', 'exp': datetime.now() + timedelta(seconds=30)}
    # create = {'id': 3, 'email': 'create@def.com', 'exp': datetime.now() + timedelta(seconds=30)}
    # update = {'id': 4, 'email': 'update@def.com', 'exp': datetime.now() + timedelta(seconds=30)}
    # user = {'id': 5, 'email': 'user@def.com', 'exp': datetime.now() + timedelta(seconds=30)}

    @classmethod
    def setUp(cls):
        CoreLib.cache_registry.unregister('test_user_security')

        cls.admin = result_to_dict(user_data_access.create({'username': 'admin', 'email': 'admin@def.com', 'role': User.PolicyRoles.ADMIN}))
        cls.delete = result_to_dict(user_data_access.create({'username': 'delete', 'email': 'delete@def.com', 'role': User.PolicyRoles.DELETE}))
        cls.create = result_to_dict(user_data_access.create({'username': 'create', 'email': 'create@def.com', 'role': User.PolicyRoles.CREATE}))
        cls.update = result_to_dict(user_data_access.create({'username': 'update', 'email': 'update@def.com', 'role': User.PolicyRoles.UPDATE}))
        cls.user = result_to_dict(user_data_access.create({'username': 'user', 'email': 'user@def.com', 'role': User.PolicyRoles.USER}))

        CoreLib.cache_registry.register('test_user_security', CacheHandlerRam())

    def _create_request(self, payload: dict):
        request_object = HttpRequest
        token = jwt.encode(payload, key)
        request_object.COOKIES = {'user_cookie': token}
        return request_object

    def test_has_access(self):
        self.assertTrue(has_access(User.PolicyRoles.ADMIN.value, [User.PolicyRoles.ADMIN.value]))
        self.assertTrue(has_access(User.PolicyRoles.DELETE.value, [User.PolicyRoles.DELETE.value]))
        self.assertTrue(has_access(User.PolicyRoles.CREATE.value, [User.PolicyRoles.CREATE.value]))
        self.assertTrue(has_access(User.PolicyRoles.UPDATE.value, [User.PolicyRoles.UPDATE.value]))
        self.assertTrue(has_access(User.PolicyRoles.USER.value, [User.PolicyRoles.USER.value]))

        self.assertFalse(has_access(User.PolicyRoles.USER.value, [User.PolicyRoles.ADMIN.value]))
        self.assertFalse(has_access(User.PolicyRoles.UPDATE.value, [User.PolicyRoles.DELETE.value]))
        self.assertFalse(has_access(User.PolicyRoles.USER.value, [User.PolicyRoles.CREATE.value]))

        self.assertTrue(has_access(User.PolicyRoles.ADMIN.value, [User.PolicyRoles.CREATE.value]))
        self.assertTrue(has_access(User.PolicyRoles.CREATE.value, [User.PolicyRoles.UPDATE.value]))
        self.assertTrue(has_access(User.PolicyRoles.UPDATE.value, [User.PolicyRoles.USER.value]))

    def test_secure_entry(self):
        # Admin
        response = admin_entry(self._create_request(TestUserSecurity.admin))
        self.assertEqual(response.status_code, 200)

        response = delete_entry(self._create_request(TestUserSecurity.admin))
        self.assertEqual(response.status_code, 200)

        response = create_entry(self._create_request(TestUserSecurity.admin))
        self.assertEqual(response.status_code, 200)

        response = update_entry(self._create_request(TestUserSecurity.admin))
        self.assertEqual(response.status_code, 200)

        response = user_entry(self._create_request(TestUserSecurity.admin))
        self.assertEqual(response.status_code, 200)

        # Delete
        response = admin_entry(self._create_request(TestUserSecurity.delete))
        self.assertEqual(response.status_code, 401)

        response = delete_entry(self._create_request(TestUserSecurity.delete))
        self.assertEqual(response.status_code, 200)

        response = create_entry(self._create_request(TestUserSecurity.delete))
        self.assertEqual(response.status_code, 200)

        response = update_entry(self._create_request(TestUserSecurity.delete))
        self.assertEqual(response.status_code, 200)

        response = user_entry(self._create_request(TestUserSecurity.delete))
        self.assertEqual(response.status_code, 200)

        # Create
        response = admin_entry(self._create_request(TestUserSecurity.create))
        self.assertEqual(response.status_code, 401)

        response = delete_entry(self._create_request(TestUserSecurity.create))
        self.assertEqual(response.status_code, 401)

        response = create_entry(self._create_request(TestUserSecurity.create))
        self.assertEqual(response.status_code, 200)

        response = update_entry(self._create_request(TestUserSecurity.create))
        self.assertEqual(response.status_code, 200)

        response = user_entry(self._create_request(TestUserSecurity.create))
        self.assertEqual(response.status_code, 200)

        # Update
        response = admin_entry(self._create_request(TestUserSecurity.update))
        self.assertEqual(response.status_code, 401)

        response = delete_entry(self._create_request(TestUserSecurity.update))
        self.assertEqual(response.status_code, 401)

        response = create_entry(self._create_request(TestUserSecurity.update))
        self.assertEqual(response.status_code, 401)

        response = update_entry(self._create_request(TestUserSecurity.update))
        self.assertEqual(response.status_code, 200)

        response = user_entry(self._create_request(TestUserSecurity.update))
        self.assertEqual(response.status_code, 200)

        # User
        response = admin_entry(self._create_request(TestUserSecurity.user))
        self.assertEqual(response.status_code, 401)

        response = delete_entry(self._create_request(TestUserSecurity.user))
        self.assertEqual(response.status_code, 401)

        response = create_entry(self._create_request(TestUserSecurity.user))
        self.assertEqual(response.status_code, 401)

        response = update_entry(self._create_request(TestUserSecurity.user))
        self.assertEqual(response.status_code, 401)

        response = user_entry(self._create_request(TestUserSecurity.user))
        self.assertEqual(response.status_code, 200)

    def test_expiry(self):
        request = self._create_request(TestUserSecurity.admin)

        response = no_policy_entry(request)
        self.assertEqual(response.status_code, 200)

        response = no_policy_entry(request)
        self.assertEqual(response.status_code, 200)

        with freeze_time(datetime.now() + timedelta(seconds=31)):
            with self.assertLogs():
                with self.assertRaises(ExpiredSignatureError):
                    response = no_policy_entry(request)
                    self.assertEqual(response.status_code, 200)

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


@RequireLogin(policies=[User.PolicyRoles.ADMIN.value])
@handle_exceptions
def admin_entry(request):
    pass


@RequireLogin(policies=[User.PolicyRoles.DELETE.value])
@handle_exceptions
def delete_entry(request):
    pass


@RequireLogin(policies=[User.PolicyRoles.CREATE.value])
@handle_exceptions
def create_entry(request):
    pass


@RequireLogin(policies=[User.PolicyRoles.UPDATE.value])
@handle_exceptions
def update_entry(request):
    pass


@RequireLogin(policies=[User.PolicyRoles.USER.value])
@handle_exceptions
def user_entry(request):
    pass


@RequireLogin(policies=[])
@handle_exceptions
def no_policy_entry(request):
    pass
