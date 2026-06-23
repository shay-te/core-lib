import logging
from abc import ABC, abstractmethod
from core_lib.session.token_handler import TokenHandler
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils


class UserSecurity(ABC):
    def __init__(self, cookie_name: str, token_handler: TokenHandler):
        """
        Initialize a UserSecurity instance with authentication token handling.
        
        Parameters:
        	cookie_name (str): The name of the cookie for storing the authentication token. Must be non-empty.
        	token_handler (TokenHandler): The handler for encoding and decoding tokens.
        
        Raises:
        	AssertionError: If cookie_name is empty or falsy.
        """
        if not cookie_name:
            raise AssertionError('UserSecurity: cookie_name is required')
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
        """
        Encode an object as a session token.
        
        Parameters:
            obj: An object to encode as a session token.
        
        Returns:
            The encoded token.
        """
        return self.token_handler.encode(self.generate_session_data(obj))

    def token_to_session_object(self, token):
        # Catch Exception (not BaseException) so SystemExit / KeyboardInterrupt
        # propagate normally.
        """
        Convert an encoded token to a session object.
        
        Parameters:
            token: The encoded token to decode.
        
        Returns:
            The session object if decoding succeeds, None otherwise.
        """
        try:
            session_data = self.token_handler.decode(token)
            if session_data:
                return self.from_session_data(session_data)
        except Exception as ex:
            self.logger.error(ex)
        return None

    def _secure_entry(self, request, policies):
        """
        Internal entry point for processing requests with security policies.
        
        Extracts and decodes the authentication token from request cookies, then delegates to secure_entry for request processing.
        """
        cookies = {}
        if WebHelpersUtils.get_server_type() == WebHelpersUtils.ServerType.DJANGO:
            cookies = request.COOKIES
        elif WebHelpersUtils.get_server_type() == WebHelpersUtils.ServerType.FLASK:
            cookies = request.cookies
        token = cookies.get(self.cookie_name)
        session_obj = self.from_session_data(self.token_handler.decode(token)) if token else None
        return self.secure_entry(request, session_obj, policies)
