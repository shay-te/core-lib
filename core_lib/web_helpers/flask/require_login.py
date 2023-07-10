from functools import wraps
import logging
from flask import request
from core_lib.web_helpers.helpers import require_login_helper
logger = logging.getLogger(__name__)


class RequireLogin(object):
    def __init__(self, policies=None):
        if policies is None:
            policies = []
        self.policies = policies

    def __call__(self, func, *args, **kwargs):
        @wraps(func)
        def __wrapper(*args, **kwargs):
            return require_login_helper(request, self.policies, func, *args, **kwargs)
        return __wrapper
