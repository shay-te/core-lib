import logging
import os
from abc import ABC, abstractmethod
from core_lib.session.token_handler import TokenHandler
import jwt


class UserSecurity(ABC):
    def __init__(self, cookie_name: str, token_handler: TokenHandler):
        assert cookie_name
        self.cookie_name = cookie_name
        self.logger = logging.getLogger(self.__class__.__name__)
        self.token_handler = token_handler

    @abstractmethod
    def secure_entry(self, request, session_obj, policies: list):
        pass

    # Convert generated session data to Session Object
    @abstractmethod
    def from_session_data(self, session_data: dict):
        pass

    @abstractmethod
    def generate_session_data(self, obj) -> dict:
        pass

    def generate_session_data_token(self, obj):
        return self.token_handler.encode(self.generate_session_data(obj))

    def token_to_session_object(self, token):
        try:
            session_data = self.token_handler.decode(token)
            if session_data:
                return self.from_session_data(session_data)
        except BaseException as ex:
            self.logger.error(ex)
            return None

    def _secure_entry(self, request, policies, frame_work_type='django'):
        if frame_work_type == 'django':
            session_obj = None
            if self.cookie_name in request.COOKIES:
                token = request.COOKIES[self.cookie_name]
                session_obj = self.from_session_data(self.token_handler.decode(token))
            return self.secure_entry(request, session_obj, policies)
        else:
            session_obj = None
            if request.cookies.get(self.cookie_name):
                token = request.cookies.get(self.cookie_name)
                session_obj = jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms=["HS256"])
            return self.secure_entry(request, session_obj, policies)

