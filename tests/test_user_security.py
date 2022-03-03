import enum
import json
import unittest
from abc import ABC
from datetime import timedelta, datetime
from http import HTTPStatus

import jwt
from django.conf import settings
from django.http import HttpRequest
from sqlalchemy import Integer, Column, VARCHAR

from core_lib.data_layers.data.db.sqlalchemy.base import Base
from core_lib.data_layers.data_access.db.crud.crud import CRUD
from core_lib.data_layers.data_access.db.crud.crud_data_access import CRUDDataAccess
from core_lib.data_transform.result_to_dict import result_to_dict
from core_lib.rule_validator.rule_validator import ValueRuleValidator, RuleValidator
from core_lib.session.jwt_token_handler import JWTTokenHandler
from core_lib.session.security_handler import SecurityHandler
from core_lib.session.user_security import UserSecurity
from core_lib.web_helpers.decorators import handle_exceptions
from core_lib.web_helpers.django.decorators import RequireLogin
from core_lib.web_helpers.request_response_helpers import response_message
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
from tests.test_data.test_utils import connect_to_mem_db


# CRUD SETUP
class User(Base):
    __tablename__ = 'user_security'

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(VARCHAR(length=255), nullable=False, default="")
    email = Column(VARCHAR(length=255), nullable=False, default="")
    role = Column(Integer, nullable=False)


class UserDataAccess(CRUDDataAccess):
    allowed_update_types = [
        ValueRuleValidator('username', str),
        ValueRuleValidator('email', str),
        ValueRuleValidator('role', int),
    ]

    rules_validator = RuleValidator(allowed_update_types)

    def __init__(self):
        CRUD.__init__(self, User, connect_to_mem_db(), UserDataAccess.rules_validator)


# USER SECURITY SETUP
class PolicyRoles(enum.Enum):
    USER = 1
    TESTER = 2
    ADMIN = 3


class SessionUser(object):

    def __init__(self, id: int, email: str):
        self.id = id
        self.email = email

    def __dict__(self):
        return {'id': self.id, 'email': self.email}


class CustomerSecurity(UserSecurity):

    def __init__(self, cookie_name: str, secret: str, expiration_time: timedelta):
        UserSecurity.__init__(self, cookie_name, JWTTokenHandler(secret, expiration_time))

    def secure_entry(self, request, session_obj: SessionUser, policies: list):
        data_dict = result_to_dict(user_data_access.get(session_obj.id))
        if data_dict['email'] == session_obj.email:
            if data_dict['role'] == policies[0].value:
                return response_message('THIS IS A ADMIN PAGE', HTTPStatus.UNAUTHORIZED)
            else:
                return response_message('OK', HTTPStatus.OK)
        else:
            return response_message('CREDENTIALS NOT MATCHED', HTTPStatus.FORBIDDEN)

    def from_session_data(self, session_data: dict) -> SessionUser:
        return SessionUser(session_data['id'], session_data['email'])

    def generate_session_data(self, user) -> dict:
        return {
            'id': user['id'],
            'email': user['email'],
        }


# CRUD INIT
user_data_access = UserDataAccess()

# SECURITY HANDLER REGISTER
key = 'super-secret'
security_handler = CustomerSecurity('user_cookie', key, timedelta(seconds=2))
SecurityHandler.register(security_handler)

# DJANGO INIT
settings.configure()
settings.DEFAULT_CHARSET = 'utf-8'
web_util = WebHelpersUtils()
web_util.init(web_util.ServerType.DJANGO)


class TestUserSecurity(unittest.TestCase):

    @classmethod
    def setUp(cls):
        user_data_access.create({'username': 'user_1', 'email': 'user_1@def.com', 'role': 1})
        user_data_access.create({'username': 'user_2', 'email': 'user_2@def.com', 'role': 2})
        user_data_access.create({'username': 'user_3', 'email': 'user_3@def.com', 'role': 3})

    def test_secure_entry(self):
        request_object = HttpRequest
        payload = {'id': 2, 'email': 'user_1@def.com'}
        token = jwt.encode(payload, key)
        request_object.COOKIES = {'user_cookie': token}

        resp_msg = user_entry(request_object)
        self.assertEqual(resp_msg.status_code, 403)
        resp_msg_data = json.loads(resp_msg.content.decode('utf-8'))
        self.assertEqual(resp_msg_data['message'], 'CREDENTIALS NOT MATCHED')

        request_object = HttpRequest
        payload = {'id': 2, 'email': 'user_2@def.com'}
        token = jwt.encode(payload, key)
        request_object.COOKIES = {'user_cookie': token}

        resp_msg = user_entry(request_object)
        self.assertEqual(resp_msg.status_code, 200)
        resp_msg_data = json.loads(resp_msg.content.decode('utf-8'))
        self.assertEqual(resp_msg_data['message'], 'OK')

        request_object = HttpRequest
        payload = {'id': 3, 'email': 'user_3@def.com'}
        token = jwt.encode(payload, key)
        request_object.COOKIES = {'user_cookie': token}

        resp_msg = user_entry(request_object)
        self.assertEqual(resp_msg.status_code, 200)
        resp_msg_data = json.loads(resp_msg.content.decode('utf-8'))
        self.assertEqual(resp_msg_data['message'], 'OK')

        request_object = HttpRequest
        payload = {'id': 1, 'email': 'user_1@def.com'}
        token = jwt.encode(payload, key)
        request_object.COOKIES = {'user_cookie': token}

        resp_msg = user_entry(request_object)
        self.assertEqual(resp_msg.status_code, 401)
        resp_msg_data = json.loads(resp_msg.content.decode('utf-8'))
        self.assertEqual(resp_msg_data['message'], 'THIS IS A ADMIN PAGE')

    def test_session_data(self):
        time_stamp = datetime.utcnow().timestamp()
        user = result_to_dict(user_data_access.get(1))
        user_session = SecurityHandler.get().generate_session_data_token(user)
        decoded_dict = jwt.decode(user_session, options={"verify_signature": False})

        self.assertIsInstance(decoded_dict, dict)
        self.assertEqual(decoded_dict['id'], user['id'])
        self.assertEqual(decoded_dict['email'], user['email'])
        self.assertGreater(decoded_dict['exp'], time_stamp)
        print('JWT EXP', decoded_dict['exp'])
        print('TIMESTAMP', time_stamp)


@RequireLogin(policies=[PolicyRoles.USER, PolicyRoles.TESTER, PolicyRoles.ADMIN])
@handle_exceptions
def user_entry(request):
    pass

# create user entry for admin tester user and both