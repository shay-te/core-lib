from functools import wraps
from core_lib.session.security_handler import SecurityHandler
import logging

from core_lib.web_helpers.decorators import handle_exception

logger = logging.getLogger(__name__)


class RequireLogin(object):
    def __init__(self, policies: list = []):
        self.policies = policies

    def __call__(self, func, *args, **kwargs):
        @wraps(func)
        def __wrapper(request, *args, **kwargs):
            response = handle_exception(SecurityHandler.get()._secure_entry, request, self.policies)
            if not response:
                try:
                    return func(request, *args, **kwargs)
                except Exception:
                    logger.error(
                        f'error while loading target page for controller entry name `{func.__name__}`', exc_info=True
                    )
            return response

        return __wrapper