import logging
import traceback
from functools import wraps
from http import HTTPStatus

from core_lib.core_lib import CoreLib

from core_lib.web_helpers.web_helpers_utils import WebHelpersUtils
from jwt import ExpiredSignatureError

from core_lib.error_handling.status_code_exception import StatusCodeException
from core_lib.web_helpers.request_response_helpers import response_message

logger = logging.getLogger(__name__)

def _get_request():
    # The request the error middlewares see. Flask keeps the current one in a global; Django hands it only to
    # the view, so there is none to give.
    try:
        server_type = WebHelpersUtils.get_server_type()
    except ValueError as e:
        logger.debug(f"Unable to determine server type: {e}")
        return None
    if server_type == WebHelpersUtils.ServerType.FLASK:
        from flask import request as flask_request
        return flask_request
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


def _framework_http_status(exc):
    # The web framework's own HTTP errors (Flask's abort(404), Django's Http404) keep the status the
    # framework would answer them with. Imported lazily: an app installs only its own framework.
    server_type = WebHelpersUtils.get_server_type()
    if server_type == WebHelpersUtils.ServerType.FLASK:
        from werkzeug.exceptions import HTTPException
        if isinstance(exc, HTTPException) and exc.code:
            return exc.code
    else:  # Django: init() accepts only the two server types
        from django.core.exceptions import BadRequest, PermissionDenied, SuspiciousOperation
        from django.http import Http404
        if isinstance(exc, Http404):
            return HTTPStatus.NOT_FOUND
        if isinstance(exc, PermissionDenied):
            return HTTPStatus.FORBIDDEN
        if isinstance(exc, (BadRequest, SuspiciousOperation)):
            return HTTPStatus.BAD_REQUEST
    return None


def _get_exception_status_code(exc):
    if isinstance(exc, StatusCodeException):
        return response_message(status=exc.status_code)
    elif isinstance(exc, ExpiredSignatureError):
        return response_message(status=HTTPStatus.UNAUTHORIZED)
    elif isinstance(exc, AssertionError):
        return response_message(status=HTTPStatus.INTERNAL_SERVER_ERROR)
    else:
        return response_message(status=_framework_http_status(exc) or HTTPStatus.INTERNAL_SERVER_ERROR)

def handle_exception(func, *args, **kwargs):
    log_exception = kwargs.pop("log_exception", True)

    try:
        return func(*args, **kwargs)

    except (StatusCodeException, AssertionError, ExpiredSignatureError, BaseException) as exc:
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
