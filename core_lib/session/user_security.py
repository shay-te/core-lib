import logging
from abc import ABC, abstractmethod
from http import HTTPStatus
from core_lib.session.token_handler import TokenHandler
from core_lib.web_helpers.request_response_helpers import response_status
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils


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

    def _secure_entry(self, request, policies):
        cookies = {}
        if WebHelpersUtils.get_server_type() == WebHelpersUtils.ServerType.DJANGO:
            cookies = request.COOKIES
        elif WebHelpersUtils.get_server_type() == WebHelpersUtils.ServerType.FLASK:
            cookies = request.cookies
        token = cookies.get(self.cookie_name)
        session_obj = self.from_session_data(self.token_handler.decode(token)) if token else None
        return self.secure_entry(request, session_obj, policies)
