---
id: handle_exceptions
title: HandleException Decorator
sidebar: core_lib_doc_sidebar
permalink: handle_exceptions.html
folder: core_lib_doc
toc: false
---

Without centralized exception handling, every API endpoint needs its own `try/except` to turn exceptions into HTTP responses. `HandleException` does this in one decorator — it catches the exception, logs it, and returns the right HTTP status automatically.

*core_lib.web_helpers.decorators.HandleException* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/decorators.py#L34){:target="_blank"}

```python
class HandleException(object):
    def __init__(self, log_exception: bool = True):
```

- **`log_exception`** *`(bool)`*: Default `True`. When `False`, the exception is still caught and converted to an HTTP response but is not logged.

>Can be configured with `Flask` and `Django` with the help of `Core-Lib`'s `WebHelpersUtils`.

Can handle exceptions for:
- `StatusCodeException` a part of `Core-Lib`'s `error_handling` class, raises a `StatusCodeException` with the given `status_code` if the user wants to return a different status code.
- `AssertionError` returns a response with `Status Code 500` when an assertion fails.
- `BaseException` returns a response with `Status Code 500` when any other exceptions are raised.
- `ExpiredSignatureError` returns a response with `Status Code 401` while attempting to decode a jwt expired token using the `JWTTokenHandler`.


**Example**

```python
from http import HTTPStatus

from core_lib.web_helpers.decorators import HandleException
from core_lib.error_handling.status_code_exception import StatusCodeException
from core_lib.web_helpers.request_response_helpers import response_json

@HandleException()
def get_user(request):
    # if this query fails decorator will log the entire Exception message and return HTTP Response with status code 500
    return response_json(example_core_lib.user.get(request.user.user_id))

get_user(request)  # get the HTTP response as per the execution of query.

user_status = 'inactive'
@HandleException()
def check_active(user_id):
    # decorator will log the AssertionError message and return HTTP Response with status code 500
    assert user_status == 'active'

@HandleException()
def validate_user(user_id):
    ...
    if not user_validate:
        # decorator will log the StatusCodeException message and return HTTP response with status_code 401 for unauthorized
        raise StatusCodeException(HTTPStatus.UNAUTHORIZED)
```

## handle_exception Function

*core_lib.web_helpers.decorators.handle_exception()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/decorators.py#L13){:target="_blank"}

`handle_exception` function is also being used by the `HandleException` decorator, this function is responsible for
returning HTTP response for the raised exception.

```python
def handle_exception(func, *args, **kwargs):
```
**Arguments**

- **`func`**: The function on which we need to handle exceptions.  
- __`*args, **kwargs`__: The args and kwargs of the function.

**Example**
```python
from http import HTTPStatus

from core_lib.web_helpers.decorators import handle_exception
from core_lib.error_handling.status_code_exception import StatusCodeException
from core_lib.web_helpers.request_response_helpers import response_json

def get_user(request):
    # if this query fails function will log the entire Exception message and return HTTP Response with status code 500
    return response_json(example_core_lib.user.get(request.user.user_id))

handle_exception(get_user, request)  # get the HTTP response as per the execution of query.

user_status = 'inactive'
def check_active(user_id):
    assert user_status == 'active'

handle_exception(check_active, 1)  # function will log the AssertionError message and return HTTP Response with status code 500

def validate_user(user_id):
    ...
    if not user_validate:
        raise StatusCodeException(HTTPStatus.UNAUTHORIZED)

handle_exception(validate_user, 1)  # function will log the StatusCodeException message and return HTTP response with status_code 401 for unauthorized
```

## Exception Middleware Hook

Every exception caught by `HandleException` or `handle_exception` also fires `CoreLib.handle_exception_middleware` — a `MiddlewareChain` that runs before the HTTP response is returned. Use this to plug in cross-cutting error handling: Sentry reporting, custom audit logs, alerting.

`CoreLib.handle_exception_middleware` is a class-level `MiddlewareChain`. Add to it once during startup.

```python
from core_lib.core_lib import CoreLib
from core_lib.middleware.middleware import Middleware


class SentryMiddleware(Middleware):
    def handle(self, context) -> None:
        # context keys: exc, func, request, stacktrace
        import sentry_sdk
        sentry_sdk.capture_exception(context['exc'])


CoreLib.handle_exception_middleware.add(SentryMiddleware())
```

**Context dict passed to each middleware:**

- **`exc`**: The caught exception instance.
- **`func`**: The decorated function that raised it.
- **`request`**: The current request object (Flask only; `None` for Django).
- **`stacktrace`** *`(str)`*: Formatted traceback string.

If a middleware itself raises an exception, it is logged as a warning and the chain continues — it does not suppress the original HTTP error response.

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/user_security.html"><< Previous</a></button>
    <button class="pageNext-btn"><a href="/web.html">Next >></a></button>
</div>