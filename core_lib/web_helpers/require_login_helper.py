from core_lib.session.security_handler import SecurityHandler
from core_lib.web_helpers.decorators import handle_exception
import logging
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils

logger = logging.getLogger(__name__)


def require_login(request, policies, func, *args, **kwargs):
    """
    Enforce authorization and conditionally invoke a function with exception handling.
    
    Checks authorization for the given request and policies. If authorization fails, 
    returns the failure response. If authorization passes, invokes the provided function 
    and converts any exceptions into HTTP responses.
    
    Parameters:
        request: The HTTP request object.
        policies: Authorization policies to enforce.
        func: The callable to invoke if authorization passes.
        *args: Positional arguments to pass to func.
        **kwargs: Keyword arguments to pass to func.
    
    Returns:
        HTTP response indicating authorization failure, or the result of calling func.
    """
    response = handle_exception(SecurityHandler.get()._secure_entry, request, policies)
    if not response:
        # Route the view function through handle_exception so its exceptions
        # become proper HTTP responses (rather than being silently swallowed
        # and returning None — which previously rendered as a blank page).
        if WebHelpersUtils.get_server_type() == WebHelpersUtils.ServerType.DJANGO:
            return handle_exception(func, request, *args, **kwargs)
        return handle_exception(func, *args, **kwargs)
    return response
