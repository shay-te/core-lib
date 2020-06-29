import logging
from abc import ABC, abstractmethod
from core_lib.session.session_manager import SessionManager


class UserSecurity(ABC):

    def __init__(self, cookie_name):
        self.cookie_name = cookie_name
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def secure_entry(self, request, session_obj, policies: list):
        pass

    @abstractmethod
    def to_session_object(self, session_data: dict):
        pass

    @abstractmethod
    def to_session_data(self, obj) -> dict:
        pass

    def user_object_to_token(self, obj):
        return SessionManager.get().encode(self.to_session_data(obj))

    def token_to_session_object(self, token):
        session_data = SessionManager.get().decode(token)
        if session_data:
            return self.to_session_object(session_data)

    def _secure_entry(self, request, policies):
        session_obj = None
        if self.cookie_name in request.COOKIES:
            token = request.COOKIES[self.cookie_name]
            session_obj = self.to_session_object(SessionManager.get().decode(token))
        return self.secure_entry(request, session_obj, policies)
