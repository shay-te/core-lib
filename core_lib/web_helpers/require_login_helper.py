from core_lib.session.security_handler import SecurityHandler
from core_lib.web_helpers.decorators import handle_exception
import logging
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils

logger = logging.getLogger(__name__)


def require_login(request, policies, func, *args, **kwargs):
    response = handle_exception(SecurityHandler.get()._secure_entry, request, policies)
    if not response:
<<<<<<< Updated upstream
        try:
            if WebHelpersUtils.get_server_type() == WebHelpersUtils.ServerType.DJANGO:
                return func(request, *args, **kwargs)
            else:
                return func(*args, **kwargs)
        except Exception:
            logger.error(
                f'error while loading target page for controller entry name `{func.__name__}`', exc_info=True
            )
=======
        # Route the view function through handle_exception so its exceptions
        # become proper HTTP responses (rather than being silently swallowed
        # and returning None — which previously rendered as a blank page).
        # Django and FastAPI views receive the request as a positional arg
        # (Django convention; FastAPI via this lib's RequireLogin wrapper).
        # Flask views read the request from a thread-local proxy so it isn't
        # passed positionally.
        server_type = WebHelpersUtils.get_server_type()
        if server_type in (
            WebHelpersUtils.ServerType.DJANGO,
            WebHelpersUtils.ServerType.FASTAPI,
        ):
            return handle_exception(func, request, *args, **kwargs)
        return handle_exception(func, *args, **kwargs)
>>>>>>> Stashed changes
    return response
