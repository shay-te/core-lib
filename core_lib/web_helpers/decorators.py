import logging
import traceback
from functools import wraps
from http import HTTPStatus

from core_lib.core_lib import CoreLib

from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
from jwt import ExpiredSignatureError

from core_lib.error_handling.status_code_exception import StatusCodeException
from core_lib.web_helpers.request_response_helpers import response_message

logger = logging.getLogger(__name__)

def _get_request():
    # Best-effort lookup of the current request for error-middleware context.
    # Flask exposes a thread-local proxy; Django does not, so this function
    # returns None for Django (callers are expected to pass the request via
    # the middleware context instead).
    try:
        server_type = WebHelpersUtils.get_server_type()
    except Exception as e:
        logger.debug(f"Unable to determine server type: {e}")
        return None

    if server_type == WebHelpersUtils.ServerType.FLASK:
        try:
            from flask import request as flask_request
            return flask_request
        except Exception as e:
            logger.debug(f"Failed to fetch Flask request: {e}")
            return None
    # DJANGO and any unknown server type: no thread-local request available.
    return None

def _execute_error_middlewares(exc, func):
    request = _get_request()

    context = {
        "exc": exc,
        "func": func,
        "request": request,
        "stacktrace": traceback.format_exc(),
    }

    try:
        CoreLib.handle_exception_middleware.execute(context)
    except Exception as mw_exc:
        logger.warning(f"Error while executing error middlewares: {mw_exc}", exc_info=True)


def _get_exception_status_code(exc):
    if isinstance(exc, StatusCodeException):
        return response_message(status=exc.status_code)
    elif isinstance(exc, ExpiredSignatureError):
        return response_message(status=HTTPStatus.UNAUTHORIZED)
    elif isinstance(exc, AssertionError):
        return response_message(status=HTTPStatus.INTERNAL_SERVER_ERROR)
    else:
        return response_message(status=HTTPStatus.INTERNAL_SERVER_ERROR)

def handle_exception(func, *args, **kwargs):
    log_exception = kwargs.pop("log_exception", True)

    try:
        return func(*args, **kwargs)

    # Catch Exception (not BaseException) so SystemExit / KeyboardInterrupt /
    # GeneratorExit propagate normally — letting Ctrl-C / shutdown signals
    # actually shut the worker down. The other classes listed are all
    # Exception subclasses; listing them is informational only.
    except (StatusCodeException, AssertionError, ExpiredSignatureError, Exception) as exc:
        # Run middlewares on all failures
        _execute_error_middlewares(exc, func)

        logger.error(f"handle_exception got {type(exc).__name__} error for function `{func}`")
        logger.exception(exc, exc_info=log_exception)

        return _get_exception_status_code(exc)



class HandleException(object):
    def __init__(self, log_exception: bool = True):
        self._log_exception = log_exception

    def __call__(self, func, *args, **kwargs):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return handle_exception(func, log_exception=self._log_exception, *args, **kwargs)

        return wrapper
