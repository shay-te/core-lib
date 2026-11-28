"""@RequireLogin: one decorator for Flask, Django and FastAPI views.

The check itself is `require_login` (require_login_helper.py), which can also be called directly. The decorator
passes it the view's arguments as they came, and `require_login` finds the request in them:
- Flask: the view gets no request. `require_login` reads Flask's thread-local `request`.
- Django: the request is the view's first positional argument.
- FastAPI: a parameter named `request` (`request: Request`), anywhere in the signature. FastAPI passes every
  argument by keyword.

A view is a plain `def`, not `async def`: `require_login` refuses an `async def` view when it is called. core-lib
services are synchronous: FastAPI runs a `def` view in its thread pool, while an `async def` view would hold the
event loop, and every other request, for the whole call.
"""
from functools import wraps

from core_lib.web_helpers.require_login_helper import require_login


class RequireLogin(object):
    def __init__(self, policies=None, security_handler_name: str = None):
        if policies is None:
            policies = []
        self.policies = policies
        self.security_handler_name = security_handler_name

    def __call__(self, func, *args, **kwargs):
        @wraps(func)
        def __wrapper(*args, **kwargs):
            return require_login(self.policies, func, *args,
                                 security_handler_name=self.security_handler_name, **kwargs)

        return __wrapper
