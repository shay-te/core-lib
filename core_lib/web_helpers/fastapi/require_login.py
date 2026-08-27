"""@RequireLogin decorator for FastAPI views.

Mirrors the Flask / Django variants. FastAPI views can be async or sync;
this decorator supports both. The wrapped view must accept the Starlette
``Request`` as its first parameter (the standard FastAPI convention via
``request: Request`` parameter binding).
"""
import logging
from functools import wraps

from core_lib.web_helpers.require_login_helper import require_login

logger = logging.getLogger(__name__)


class RequireLogin(object):
    def __init__(self, policies=None):
        if policies is None:
            policies = []
        self.policies = policies

    def __call__(self, func, *args, **kwargs):
        @wraps(func)
        def __wrapper(request, *args, **kwargs):
            # `require_login` itself re-passes `request` to `func` when the
            # server type is FASTAPI (or DJANGO), so we strip it from
            # *args here and only forward the rest.
            return require_login(request, self.policies, func, *args, **kwargs)

        return __wrapper
