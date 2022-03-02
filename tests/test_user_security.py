import unittest
from abc import ABC
from datetime import timedelta

from core_lib.session.jwt_token_handler import JWTTokenHandler
from core_lib.session.user_security import UserSecurity

class SessionUser(object):

    def __init__(self, user_id: int, status: int):
        self.u_id = user_id
        self.status = status


    def __str__(self):
        return f'u_id:{self.u_id}, status: {self.status}'


class CustomerSecurity(UserSecurity, ABC):

    def __init__(self, cookie_name: str, secret: str, expiration_time: timedelta):
        UserSecurity.__init__(self, cookie_name, JWTTokenHandler(secret, expiration_time))

    def secure_entry(self, request, session_obj: SessionUser, policies: list = []):
        pass

    def from_session_data(self, session_data: dict) -> SessionUser:
        return SessionUser(session_data['u_id'], session_data['status'], )

    def generate_session_data(self, user) -> dict:
        return {
            'u_id': user['id'],
            'status': user['status'],

        }


class TestUserSecurity(unittest.TestCase):

    jwt_secret = 'eyJhbGciOiJIUzI1NiJ9.eyJSb2xlIjoiQWRtaW4iLCJJc3N1ZXIiOiJJc3N1ZXIiLCJVc2VybmFtZSI6IkphdmFJblVzZSIsImV4cCI6MTY0NjE0NTgyNiwiaWF0IjoxNjQ2MTQ1ODI2fQ.9gzcGObPJgTAcz0YD45-Z1A2XzZPqIvxqZ_hfNmGtsE'

    def test_security(self):
        cs = CustomerSecurity('cookie', TestUserSecurity.jwt_secret, timedelta(days=2))
