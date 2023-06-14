from datetime import timedelta
from http import HTTPStatus
from core_lib.session.jwt_token_handler import JWTTokenHandler
from core_lib.session.user_security import UserSecurity
from core_lib.web_helpers.request_response_helpers import response_status


class AdminSecurity(UserSecurity):
    def __init__(self, cookie_name: str, secret: str, expiration_time: timedelta):
        UserSecurity.__init__(self, cookie_name, JWTTokenHandler(secret, expiration_time))

    def secure_entry(self, request, session_obj, policies: list):
        if session_obj:
            if not policies:
                return response_status(HTTPStatus.UNAUTHORIZED)
            elif policies[0] == 1 and policies[1] == 1:
                return response_status(HTTPStatus.OK)
            else:
                return response_status(HTTPStatus.UNAUTHORIZED)
        else:
            return response_status(HTTPStatus.UNAUTHORIZED)

    def from_session_data(self, session_data: dict):
        return session_data

    def generate_session_data(self, user) -> dict:
        pass
