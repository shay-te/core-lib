from functools import wraps
from core_lib.session.security_handler import SecurityHandler
import logging

from core_lib.web_helpers.decorators import handle_exception
from flask import make_response

from core_lib.web_helpers.request_response_helpers import response_ok, response_message

logger = logging.getLogger(__name__)


class RequireLogin(object):
    def __init__(self, request, policies: list = []):
        self.policies = policies
        self.request = request

    def __call__(self, func, *args, **kwargs):
        @wraps(func)
        def __wrapper(*args, **kwargs):
            response = handle_exception(SecurityHandler.get()._secure_entry, self.request, self.policies, 'flask')
            if response.status_code == 200:
                return func(*args, **kwargs)
            else:
                return response_message('Unauthorized', 401)
        return __wrapper
