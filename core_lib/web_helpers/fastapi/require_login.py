"""@RequireLogin decorator for FastAPI views.

Mirrors the Flask / Django variants, for sync and async views alike. The view
takes the Starlette ``Request`` as a parameter named ``request``
(``request: Request``): FastAPI passes every argument by keyword, and the
wrapper reads it by that name.
"""
import inspect
from functools import wraps

from core_lib.web_helpers.decorators import handle_exception_async
from core_lib.web_helpers.require_login_helper import require_login


class RequireLogin(object):
    def __init__(self, policies=None):
        if policies is None:
            policies = []
        self.policies = policies

    def __call__(self, func, *args, **kwargs):
        if inspect.iscoroutinefunction(func):
            # The wrapper is async itself: FastAPI awaits an endpoint it sees as async, and older
            # FastAPI versions decide that from the wrapper alone, without following `__wrapped__`.
            @wraps(func)
            async def __async_wrapper(request, *args, **kwargs):
                # `require_login` returns the denial response, or the view's not-yet-awaited coroutine.
                response = require_login(request, self.policies, func, *args, **kwargs)
                if inspect.isawaitable(response):
                    return await handle_exception_async(response, func)
                return response

            return __async_wrapper

        @wraps(func)
        def __wrapper(request, *args, **kwargs):
            # `require_login` passes `request` back to `func` for FASTAPI.
            return require_login(request, self.policies, func, *args, **kwargs)

        return __wrapper
