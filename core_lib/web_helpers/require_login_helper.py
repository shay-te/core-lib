import inspect

from flask import request as flask_request

from core_lib.session.security_handler import SecurityHandler
from core_lib.web_helpers.decorators import bind_request, handle_exception, handle_exception_call
import logging
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils

logger = logging.getLogger(__name__)


def require_login(policies, func, *args, security_handler_name: str = None, **kwargs):
    """Calls `func(*args, **kwargs)` when the request in those arguments passes the security check, and returns the
    security handler's response when it does not. The whole check lives here, not in `@RequireLogin`, so a direct
    call behaves the same."""
    if inspect.iscoroutinefunction(func):
        raise TypeError(f'require_login takes a plain `def` view, not `async def`: {func.__qualname__}')
    request = _view_request(args, kwargs)
    with bind_request(request):
        response = handle_exception(SecurityHandler.get(security_handler_name)._secure_entry, request, policies)
        if not response:
            # Route the view function through handle_exception so its exceptions
            # become proper HTTP responses (rather than being silently swallowed
            # and returning None — which previously rendered as a blank page).
            # `handle_exception` would take a view parameter named `log_exception` as its own option.
            return handle_exception_call(func, args, kwargs)
        return response


def _view_request(args: tuple, kwargs: dict):
    """The request in a view's arguments. A Flask view gets none and reads Flask's thread-local `request`."""
    server_type = WebHelpersUtils.get_server_type()
    if server_type == WebHelpersUtils.ServerType.DJANGO:
        return _django_request(*args, **kwargs)
    if server_type == WebHelpersUtils.ServerType.FASTAPI:
        return _fastapi_request(*args, **kwargs)
    return flask_request


def _django_request(request, *_args, **_kwargs):
    """Django passes a view its request as the first argument."""
    return request


def _fastapi_request(*_args, request, **_kwargs):
    """FastAPI passes a view every argument by keyword, so the request comes as `request`."""
    return request
