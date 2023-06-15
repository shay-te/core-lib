from functools import wraps
from http import HTTPStatus
from core_lib.session.security_handler import SecurityHandler
import logging
from core_lib.web_helpers.decorators import handle_exception
from core_lib.web_helpers.request_response_helpers import response_message


logger = logging.getLogger(__name__)


class RequireLogin(object):
    def __init__(self, request, policies: list = []):
        self.policies = policies
        self.request = request

    def __call__(self, func, *args, **kwargs):
        @wraps(func)
        def __wrapper(*args, **kwargs):
            response = handle_exception(SecurityHandler.get()._secure_entry, self.request, self.policies)
            if response.status_code == HTTPStatus.OK:
                return func(*args, **kwargs)
            else:
                return response_message('Unauthorized', HTTPStatus.UNAUTHORIZED)
        return __wrapper
