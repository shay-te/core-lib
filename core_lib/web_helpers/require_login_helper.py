from core_lib.session.security_handler import SecurityHandler
from core_lib.web_helpers.decorators import handle_exception
import logging
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils

logger = logging.getLogger(__name__)


def require_login(request, policies, func, *args, **kwargs):
    response = handle_exception(SecurityHandler.get()._secure_entry, request, policies)
    if not response:
        # Route the view function through handle_exception so its exceptions
        # become proper HTTP responses (rather than being silently swallowed
        # and returning None — which previously rendered as a blank page).
        if WebHelpersUtils.get_server_type() == WebHelpersUtils.ServerType.DJANGO:
            return handle_exception(func, request, *args, **kwargs)
        return handle_exception(func, *args, **kwargs)
    return response
