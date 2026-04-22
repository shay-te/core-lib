from functools import wraps
import logging

from core_lib.web_helpers.require_login_helper import require_login
logger = logging.getLogger(__name__)


class RequireLogin(object):
    def __init__(self, policies=None):
        if policies is None:
            policies = []
        self.policies = policies

    def __call__(self, func, *args, **kwargs):
        @wraps(func)
        def __wrapper(*args, **kwargs):
            try:
                from flask import request
            except ImportError:
                raise ImportError("pip install flask to use Flask login helpers")
            return require_login(request, self.policies, func, *args, **kwargs)

        return __wrapper
