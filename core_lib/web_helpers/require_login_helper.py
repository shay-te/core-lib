from core_lib.session.security_handler import SecurityHandler
from core_lib.web_helpers.decorators import handle_exception
import logging
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils

logger = logging.getLogger(__name__)


def require_login(request, policies, func, *args, **kwargs):
    response = handle_exception(SecurityHandler.get()._secure_entry, request, policies)
    if not response:
        try:
            if WebHelpersUtils.get_server_type() == WebHelpersUtils.ServerType.DJANGO:
                return func(request, *args, **kwargs)
            else:
                return func(*args, **kwargs)
        except Exception:
            logger.error(
                f'error while loading target page for controller entry name `{func.__name__}`', exc_info=True
            )
    return response
