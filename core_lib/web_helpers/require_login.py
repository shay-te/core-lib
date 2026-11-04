"""@RequireLogin: one decorator for Flask, Django and FastAPI views.

It finds the request the way each framework hands it over, then runs `require_login`:
- Flask: the view gets no request. The decorator reads Flask's thread-local `request`.
- Django: the request is the view's first positional argument.
- FastAPI: a parameter named `request` (`request: Request`), anywhere in the signature. FastAPI passes every
  argument by keyword.

A view is a plain `def`, not `async def`. core-lib services are synchronous: FastAPI runs a `def` view in its
thread pool, while an `async def` view would hold the event loop, and every other request, for the whole call.
"""
import inspect
from functools import wraps

from flask import request as flask_request

from core_lib.web_helpers.decorators import bind_request
from core_lib.web_helpers.require_login_helper import require_login
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils


class RequireLogin(object):
    def __init__(self, policies=None, security_handler_name: str = None):
        if policies is None:
            policies = []
        self.policies = policies
        self.security_handler_name = security_handler_name

    def __call__(self, func, *args, **kwargs):
        if inspect.iscoroutinefunction(func):
            raise TypeError(f'@RequireLogin takes a plain `def` view, not `async def`: {func.__qualname__}')

        @wraps(func)
        def __wrapper(*args, **kwargs):
            server_type = WebHelpersUtils.get_server_type()
            if server_type == WebHelpersUtils.ServerType.DJANGO:
                request, args = args[0], args[1:]
            elif server_type == WebHelpersUtils.ServerType.FASTAPI:
                request = kwargs.pop('request')
            else:
                request = flask_request
            with bind_request(request):
                return require_login(request, self.policies, func, *args,
                                     security_handler_name=self.security_handler_name, **kwargs)

        return __wrapper
