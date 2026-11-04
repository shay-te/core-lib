import inspect

from core_lib.session.security_handler import SecurityHandler
from core_lib.web_helpers.decorators import bind_request, handle_exception, handle_exception_call
import logging
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils

logger = logging.getLogger(__name__)


def assert_def_view(func):
    """`require_login` runs a plain `def` view. `@RequireLogin` also calls this when it decorates a view, so an
    `async def` one fails when the app starts, not on its first request."""
    if inspect.iscoroutinefunction(func):
        raise TypeError(f'require_login takes a plain `def` view, not `async def`: {func.__qualname__}')


def require_login(request, policies, func, *args, security_handler_name: str = None, **kwargs):
    # The whole check lives here, not in `@RequireLogin`, so a direct call gets the same behaviour.
    assert_def_view(func)
    with bind_request(request):
        response = handle_exception(SecurityHandler.get(security_handler_name)._secure_entry, request, policies)
        if not response:
            # Route the view function through handle_exception so its exceptions
            # become proper HTTP responses (rather than being silently swallowed
            # and returning None — which previously rendered as a blank page).
            # A Django view takes the request as its first positional arg. A FastAPI view
            # gets it by keyword, as FastAPI calls every view, so `request` may sit anywhere
            # in its signature. Flask views read the request from a thread-local proxy so
            # it isn't passed at all.
            server_type = WebHelpersUtils.get_server_type()
            if server_type == WebHelpersUtils.ServerType.DJANGO:
                return handle_exception(func, request, *args, **kwargs)
            if server_type == WebHelpersUtils.ServerType.FASTAPI:
                # `handle_exception` would take a view parameter named `log_exception` as its own option.
                return handle_exception_call(func, args, dict(kwargs, request=request))
            return handle_exception(func, *args, **kwargs)
        return response
