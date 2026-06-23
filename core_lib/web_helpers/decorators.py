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
    """
    Retrieve the current HTTP request object from the thread-local context, if available.
    
    For Flask applications, returns the Flask request object. For Django, unknown
    server types, or if server-type detection fails, returns None.
    
    Returns:
    	The Flask request object for Flask applications, None otherwise.
    """
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
    """
    Execute centralized exception-handling middleware with execution context.
    
    Parameters:
    	exc (Exception): The exception that was caught
    	func (callable): The function that was being executed when the exception occurred
    """
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
    """
    Map an exception to an HTTP error response with appropriate status code.
    
    Returns a response message where StatusCodeException uses its own status code,
    ExpiredSignatureError maps to 401, and other exceptions map to 500.
    
    Returns:
        A response message with the corresponding HTTP status code.
    """
    if isinstance(exc, StatusCodeException):
        return response_message(status=exc.status_code)
    elif isinstance(exc, ExpiredSignatureError):
        return response_message(status=HTTPStatus.UNAUTHORIZED)
    elif isinstance(exc, AssertionError):
        return response_message(status=HTTPStatus.INTERNAL_SERVER_ERROR)
    else:
        return response_message(status=HTTPStatus.INTERNAL_SERVER_ERROR)

_HANDLE_EXCEPTION_LOG_SENTINEL = '__handle_exception_log_flag__'


def handle_exception(func, *args, **kwargs):
    # Pop a private, sentinel-named flag so we don't clobber a user-provided
    # `log_exception` kwarg on the wrapped function. Previously this used
    # `kwargs.pop("log_exception", True)`, which both stole a user kwarg of
    # that name and produced "got multiple values for argument" when the
    # HandleException decorator forwarded `log_exception=...`.
    """
    Execute a function and return an error response if an exception is caught.
    
    If the function executes successfully, returns its result. If an exception is caught, runs configured error middleware, logs the exception, and returns an error response. The log_exception parameter controls whether the exception traceback is included in logs.
    
    Parameters:
    	log_exception (bool, optional): If False, exception traceback is not logged. Defaults to True.
    
    Returns:
    	The return value of the wrapped function, or an error response if an exception occurs.
    """
    sentinel_present = _HANDLE_EXCEPTION_LOG_SENTINEL in kwargs
    log_exception = kwargs.pop(_HANDLE_EXCEPTION_LOG_SENTINEL, True)
    # Backwards-compat: direct callers (NOT the HandleException decorator)
    # can still pass `log_exception=` as a kwarg to control logging. When
    # the sentinel was present, leave the user's `log_exception` kwarg
    # alone so it reaches the wrapped function.
    if not sentinel_present and 'log_exception' in kwargs:
        log_exception = kwargs.pop('log_exception', True)

    try:
        return func(*args, **kwargs)

    # Catch Exception (not BaseException) so SystemExit / KeyboardInterrupt /
    # GeneratorExit propagate normally — letting Ctrl-C / shutdown signals
    # actually shut the worker down. We dispatch on the specific subtypes
    # inside `_get_exception_status_code`.
    except Exception as exc:
        # Run middlewares on all failures
        _execute_error_middlewares(exc, func)

        # `logger.exception` always attaches the active traceback. When the
        # caller asked to suppress the traceback (log_exception=False), we
        # explicitly pass `exc_info=False`. Single call → no S8572 split.
        logger.exception(
            "handle_exception got %s error for function `%s`",
            type(exc).__name__, func,
            exc_info=log_exception,
        )

        return _get_exception_status_code(exc)



class HandleException(object):
    def __init__(self, log_exception: bool = True):
        self._log_exception = log_exception

    def __call__(self, func, *args, **kwargs):
        """
        Return a wrapper that applies exception handling to the decorated function.
        
        Returns:
        	A callable wrapper of the provided function with exception handling applied.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Pass log_exception via the private sentinel so we don't shadow
            # a user kwarg named `log_exception` on the wrapped function.
            handle_kwargs = dict(kwargs)
            handle_kwargs[_HANDLE_EXCEPTION_LOG_SENTINEL] = self._log_exception
            return handle_exception(func, *args, **handle_kwargs)

        return wrapper
