from __future__ import with_statement
import contextlib
from http import HTTPStatus

from core_lib.error_handling.status_code_exception import StatusCodeException


@contextlib.contextmanager
def StatusCodeAssert(status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR, message: str = None):
    try:
        yield
    except AssertionError:
        raise StatusCodeException(status_code, message)
