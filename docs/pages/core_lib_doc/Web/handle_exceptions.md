---
id: handle_exceptions
title: HandleException Decorator
sidebar: core_lib_doc_sidebar
permalink: handle_exceptions.html
folder: core_lib_doc
toc: false
---

`@HandleException()` turns an exception raised in a Flask or Django view into a JSON error response with the right HTTP status. Without it, every view needs its own `try/except` to do that. It catches the exception, runs your error hooks (for example, reporting to Sentry), logs it, and returns a response.

Use it on route handlers, so that a `StatusCodeException` raised anywhere in your Services or DataAccess reaches the client as the status it carries. Compared with Flask's `errorhandler` or Django's exception middleware, it gives you the same status mapping and JSON body in both frameworks.

> **Where it fits:** Web edge. Put `@HandleException()` on route handlers. It is the bridge between exceptions raised in your Services/DataAccess and the HTTP response your framework returns.

*core_lib.web_helpers.decorators.HandleException* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/decorators.py){:target="_blank"}

```python
class HandleException(object):
    def __init__(self, log_exception: bool = True):
```

- **`log_exception`** *`(bool)`*: Default `True`: the exception is logged at ERROR level with its traceback. When `False`, it is still logged at ERROR level (its type and message), but without the traceback.

> **Requires `WebHelpersUtils.init()`.** Call `WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)` (or `DJANGO`) once at startup; see [Web Helpers](web.html#webhelpersutils). Without it, an exception in the decorated function escapes as `ValueError('WebHelpersUtils never initialized')` instead of becoming an HTTP 500. A function that does not raise works either way.

## What the client gets

If the function returns normally, its return value is passed through unchanged. If it raises:

| Exception | Status | Response body |
|---|---|---|
| `StatusCodeException(status, ...)` | the exception's `status_code` | `{"message": "<reason phrase>"}`, or `{"error": "<reason phrase>"}` for 500 and above |
| `jwt.ExpiredSignatureError` (an expired token from `JWTTokenHandler`) | `401` | `{"message": "Unauthorized"}` |
| `AssertionError` | `500` | `{"error": "Internal Server Error"}` |
| Anything else (any `BaseException`, including `KeyboardInterrupt`) | `500` | `{"error": "Internal Server Error"}` |

The body holds only the standard reason phrase for the status (`"Not Found"`, `"Unauthorized"`, ...). The exception's own message is written to the log, not sent to the client. To send your own message, catch the error in the view and return [`response_json()`](web.html#response_json) or [`response_error()`](web.html#response_error) yourself.

The framework's own HTTP errors fall under "anything else". Inside a decorated Flask view, `abort(404)` becomes a 500. Raise `StatusCodeException(HTTPStatus.NOT_FOUND)` instead.

## Example

`core_lib` is your `CoreLib` instance, and `core_lib.user.get()` is your user service's method that returns a user dict or `None`.

```python
from http import HTTPStatus

from flask import Flask

from core_lib.error_handling.status_code_exception import StatusCodeException
from core_lib.web_helpers.decorators import HandleException
from core_lib.web_helpers.request_response_helpers import response_json
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils

WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)
app = Flask(__name__)


@app.route('/users/<int:user_id>')
@HandleException()
def get_user(user_id: int):
    assert user_id > 0, 'user_id must be positive'  # AssertionError -> 500
    user = core_lib.user.get(user_id)               # any exception -> 500
    if user is None:
        raise StatusCodeException(HTTPStatus.NOT_FOUND, f'no user {user_id}')  # -> 404
    return response_json(user)
```

| Request | Response |
|---|---|
| `GET /users/1` (user exists) | `200 {"id": 1, "email": "ada@example.com"}` |
| `GET /users/2` (no such user) | `404 {"message": "Not Found"}`. `no user 2` appears only in the log. |
| `GET /users/0` | `500 {"error": "Internal Server Error"}` |
| `GET /users/3`, and `core_lib.user.get()` raises | `500 {"error": "Internal Server Error"}` |

The same decorator works on Django views, which take `request` as their first argument. In Flask, `@app.route` goes above `@HandleException()`. On views protected by [`@RequireLogin`](user_security.html#requirelogin-decorator), put `@HandleException()` directly under `@RequireLogin`.

## `handle_exception()` function

*core_lib.web_helpers.decorators.handle_exception()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/decorators.py){:target="_blank"}

The function form of `@HandleException`: the same conversion, but called directly. Use it when you cannot decorate the target function (a third-party callable, or one built at runtime).

```python
def handle_exception(func, *args, **kwargs):
```

**Arguments**

- **`func`**: The function to call.
- **`*args, **kwargs`**: Passed to `func`. One keyword is taken out first and not passed on: `log_exception` (default `True`), with the same meaning as on the decorator.

**Returns**

What `func` returns, or an error response as in [What the client gets](#what-the-client-gets).

**Example**

```python
from core_lib.web_helpers.decorators import handle_exception
from core_lib.web_helpers.request_response_helpers import response_json


def get_user(user_id: int):
    return response_json(core_lib.user.get(user_id))


response = handle_exception(get_user, 1)                       # get_user's response, or an error response
response = handle_exception(get_user, 1, log_exception=False)  # same, without the traceback in the log
```

## Exception Middleware Hook

Every exception caught by `@HandleException` or `handle_exception()` also runs `CoreLib.handle_exception_middleware`, a [`MiddlewareChain`](middleware.html), before the response is built. Use it for error handling that applies everywhere: Sentry reporting, audit logs, alerts. This includes the errors `@RequireLogin` turns into 401/500 responses, such as an expired token.

`CoreLib.handle_exception_middleware` is a class attribute: one chain for the whole process. Add your middleware to it once, at startup.

```python
import sentry_sdk

from core_lib.core_lib import CoreLib
from core_lib.middleware.middleware import Middleware


class SentryMiddleware(Middleware):
    def handle(self, context) -> None:
        # context keys: exc, func, request, stacktrace
        sentry_sdk.capture_exception(context['exc'])


CoreLib.handle_exception_middleware.add(SentryMiddleware())
```

**Context dict passed to each middleware:**

- **`exc`**: The caught exception.
- **`func`**: The function that raised it.
- **`request`**: The current Flask request. Always `None` on Django.
- **`stacktrace`** *`(str)`*: The formatted traceback.

If one of these middlewares raises, the middlewares after it in the chain do not run. The failure is logged as a warning, and the client still gets the normal error response. Order your middlewares with this in mind, or catch errors inside each `handle()`.

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="user_security.html">Previous</a></button>
    <button class="pageNext-btn"><a href="web.html">Next</a></button>
</div>
