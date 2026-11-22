from functools import wraps
import logging
from flask import request
from core_lib.web_helpers.require_login_helper import require_login
logger = logging.getLogger(__name__)


class RequireLogin(object):
    def __init__(self, policies=None, security_handler_name: str = None):
        if policies is None:
            policies = []
        self.policies = policies
        self.security_handler_name = security_handler_name

    def __call__(self, func, *args, **kwargs):
        @wraps(func)
        def __wrapper(*args, **kwargs):
            return require_login(request, self.policies, func, *args, security_handler_name=self.security_handler_name, **kwargs)

        return __wrapper
