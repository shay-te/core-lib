---
id: handle_exceptions
title: HandleException Decorator
sidebar: core_lib_doc_sidebar
permalink: handle_exceptions.html
folder: core_lib_doc
toc: false
---

Without centralized exception handling, every API endpoint needs its own `try/except` to turn exceptions into HTTP responses. `HandleException` does this in one decorator — it catches the exception, logs it, and returns the right HTTP status automatically.

> **Where it fits:** Web edge. Apply `@HandleException` to route handlers — it's the bridge between exceptions raised anywhere in your Services/DataAccess and the HTTP response your framework returns.

*core_lib.web_helpers.decorators.HandleException* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/decorators.py#L34){:target="_blank"}

```python
class HandleException(object):
    def __init__(self, log_exception: bool = True):
```

- **`log_exception`** *`(bool)`*: Default `True`. When `False`, the exception is still caught and converted to an HTTP response but is not logged.

>Can be configured with `Flask` and `Django` with the help of `Core-Lib`'s `WebHelpersUtils`.

Can handle exceptions for:
- `StatusCodeException` — returns a response with the status code carried on the exception.
- `AssertionError` — returns a response with status `500`.
- `ExpiredSignatureError` — returns a response with status `401` (raised by `JWTTokenHandler` when decoding an expired token).
- Any other `BaseException` — returns a response with status `500`.


**Example**

```python
from http import HTTPStatus

from core_lib.web_helpers.decorators import HandleException
from core_lib.error_handling.status_code_exception import StatusCodeException
from core_lib.web_helpers.request_response_helpers import response_json


@HandleException()
def get_user(request):
    # If user.get() raises, the decorator logs the traceback and returns status 500.
    return response_json(core_lib.user.get(request.user.id))


@HandleException()
def check_active(user_id):
    # An assertion failure is caught and returned as status 500.
    assert core_lib.user.get(user_id).status == 'active'


@HandleException()
def admin_only(user_id):
    # A StatusCodeException carries its own status — here, 401.
    if not core_lib.user.is_admin(user_id):
        raise StatusCodeException(HTTPStatus.UNAUTHORIZED)
```

## `handle_exception()` function

*core_lib.web_helpers.decorators.handle_exception()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/decorators.py#L13){:target="_blank"}

The function form of `@HandleException` — same conversion behavior, but called explicitly. Useful when you can't decorate the target function (third-party callable, dynamically built, etc.).

```python
def handle_exception(func, *args, **kwargs):
```

**Arguments**

- **`func`**: The function whose exceptions you want converted to HTTP responses.
- **`*args, **kwargs`**: Arguments forwarded to `func`.

**Example**

```python
from core_lib.web_helpers.decorators import handle_exception

def get_user(request):
    return response_json(core_lib.user.get(request.user.id))

response = handle_exception(get_user, request)
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
    <button class="pagePrevious-btn"><a href="/user_security.html">Previous</a></button>
    <button class="pageNext-btn"><a href="/web.html">Next</a></button>
</div>