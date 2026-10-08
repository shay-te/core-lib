---
id: user_security
title: User Security
sidebar: core_lib_doc_sidebar
permalink: user_security.html
folder: core_lib_doc
toc: false
---

`UserSecurity` is a small base class for cookie-based login checks in Flask or Django. You write three short methods: what goes into the login token, how to turn the token back into a user object, and who may enter a view. Core-Lib then reads the cookie, decodes the token and calls your check from the `@RequireLogin` decorator, for both frameworks.

Use it when your app logs users in with a signed token (JWT) in a cookie and you want one place for the "may this user call this view?" rule. It is a thin layer over [PyJWT](https://pyjwt.readthedocs.io){:target="_blank"} and your framework's request object. If you already use Django's auth system, Flask-Login, or another auth library, you do not need it.

> **Where it fits:** Web edge. `UserSecurity` holds your auth rules, `@RequireLogin` guards views, and `UserAuthMiddleware` (optional) makes the logged-in user available inside a view.

> On this page, **session** means the logged-in user decoded from the auth cookie. It is not a database session. See the [Glossary](glossary.html).

## How a request is checked

When a request reaches a view decorated with `@RequireLogin(policies=[...])`:

1. Core-Lib reads the cookie named `cookie_name` (from your `UserSecurity`).
2. If there is no cookie, the session object is `None`. Otherwise the token handler decodes the token and your `from_session_data()` turns the payload into a session object.
   - If the token has expired, the request gets a `401` response and your `secure_entry()` is not called.
   - If the token cannot be decoded for any other reason (bad signature, not a JWT), the request gets a `500` response and `secure_entry()` is not called.
3. Your `secure_entry(request, session_obj, policies)` decides:
   - **Return `None`** (or any falsy value) to let the request through. The view runs.
   - **Return a response** (for example `response_status(HTTPStatus.UNAUTHORIZED)`) to block it. That response is sent and the view does not run. Any response object counts as "block", even one with status 200.
   - **Raise `StatusCodeException(status)`** to block it with that status.

The 401 and 500 responses in step 2 come from [`handle_exception`](handle_exceptions.html), which `@RequireLogin` uses internally. Their bodies are `{"message": "Unauthorized"}` and `{"error": "Internal Server Error"}`.

## UserSecurity

*core_lib.session.user_security.UserSecurity* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/session/user_security.py){:target="_blank"}

An abstract class. Subclass it and implement `secure_entry()`, `from_session_data()` and `generate_session_data()`.

```python
class UserSecurity(ABC):
    def __init__(self, cookie_name: str, token_handler: TokenHandler):
```

**Arguments**

- **`cookie_name`** *`(str)`*: Name of the cookie that carries the token. Must not be empty.
- **`token_handler`** *`(TokenHandler)`*: An object with `encode(dict)` and `decode(token)` methods. You must pass one; there is no default. Core-Lib ships [`JWTTokenHandler`](#jwttokenhandler).

## Functions

### secure_entry()

*core_lib.session.user_security.UserSecurity.secure_entry()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/session/user_security.py){:target="_blank"}

You implement this. It decides whether a request may enter the view.

```python
def secure_entry(self, request, session_obj, policies: list):
```

**Arguments**

- **`request`**: The framework's request object.
- **`session_obj`**: What your `from_session_data()` returned, or `None` when the request has no auth cookie.
- **`policies`** *`(list)`*: The `policies` given to `@RequireLogin`, for example `['admin']`. An empty list when none were given.

**Returns**

`None` to allow the request. A response object to block it; that response is sent instead of running the view.

### from_session_data()

*core_lib.session.user_security.UserSecurity.from_session_data()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/session/user_security.py){:target="_blank"}

You implement this. It turns the decoded token payload into the session object your app uses.

```python
def from_session_data(self, session_data: dict):
```

**Arguments**

- **`session_data`** *`(dict)`*: The decoded token payload: the dict `generate_session_data()` returned, plus an `exp` key when you use `JWTTokenHandler`.

### generate_session_data()

*core_lib.session.user_security.UserSecurity.generate_session_data()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/session/user_security.py){:target="_blank"}

You implement this. It turns your user object into the dict that is encoded into the token.

```python
def generate_session_data(self, obj) -> dict:
```

**Arguments**

- **`obj`**: Whatever you pass to `generate_session_data_token()`, usually the user returned by your login service.

**Returns**

*`(dict)`*: The token payload. Keep it small and JSON-serializable.

### generate_session_data_token()

*core_lib.session.user_security.UserSecurity.generate_session_data_token()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/session/user_security.py){:target="_blank"}

Calls `generate_session_data(obj)` and encodes the result with the token handler. Call it at login and put the result in the cookie.

```python
def generate_session_data_token(self, obj):
```

**Arguments**

- **`obj`**: Your user object, passed on to `generate_session_data()`.

**Returns**

The encoded token. With `JWTTokenHandler` this is a `str`.

### token_to_session_object()

*core_lib.session.user_security.UserSecurity.token_to_session_object()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/session/user_security.py){:target="_blank"}

Decodes a token and returns your session object. Unlike `@RequireLogin`, it never raises: if decoding fails (expired, bad signature), it logs the error and returns `None`. `UserAuthMiddleware` uses it.

```python
def token_to_session_object(self, token):
```

### _secure_entry()

*core_lib.session.user_security.UserSecurity._secure_entry()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/session/user_security.py){:target="_blank"}

Called by `@RequireLogin`; you do not call it yourself. It reads the cookie from the request, decodes it, calls `from_session_data()`, then calls your `secure_entry()` and returns its result. Decoding errors are raised, not caught here (see [How a request is checked](#how-a-request-is-checked)).

```python
def _secure_entry(self, request, policies):
```

## JWTTokenHandler

*core_lib.session.jwt_token_handler.JWTTokenHandler* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/session/jwt_token_handler.py){:target="_blank"}

The token handler Core-Lib ships. It signs and verifies [JWT](https://jwt.io){:target="_blank"} tokens with PyJWT.

```python
class JWTTokenHandler(TokenHandler):
    def __init__(self, secret, expiration_time: timedelta, verify: bool = False, algorithm: str = 'HS256'):
```

**Arguments**

- **`secret`**: The signing key. Load it from configuration or an environment variable, never from source code. For `HS256`, use at least 32 bytes; PyJWT warns about shorter keys.
- **`expiration_time`** *`(timedelta)`*: How long a token stays valid. Required.
- **`verify`** *`(bool)`*: Ignored. PyJWT 2, the version Core-Lib installs, always checks the signature and expiry, whatever this is set to, and emits a `DeprecationWarning` for the argument on each decode.
- **`algorithm`** *`(str)`*: Default `'HS256'`.

`encode(payload)` adds an `exp` (expiry) key to the dict you pass in and returns the token as a `str`. `decode(token)` returns the payload dict. It raises `jwt.ExpiredSignatureError` for an expired token and another `jwt` exception for any other invalid token.

> **Warning: run the server in UTC.** `encode()` computes `exp` with `datetime.utcnow().timestamp()`, and Python reads that time as *local* time. On a server whose time zone is not UTC, the expiry is shifted by the UTC offset. At UTC+3 a token with `timedelta(hours=1)` is already expired when it is issued; at UTC-5 it lasts 6 hours. Set `TZ=UTC` for the server process.

## SecurityHandler

*core_lib.session.security_handler.SecurityHandler* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/session/security_handler.py){:target="_blank"}

Holds your `UserSecurity` instance for the whole process. Register it once at startup. `@RequireLogin`, `UserAuthMiddleware` and your login view reach it through `SecurityHandler.get()`.

```python
class SecurityHandler(object):
```

### `register()`

*core_lib.session.security_handler.SecurityHandler.register()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/session/security_handler.py){:target="_blank"}

Registers your `UserSecurity` instance. Calling it a second time in the same process raises `ValueError('SecurityHandler already set')`.

```python
def register(user_security: UserSecurity):
```

**Arguments**

- **`user_security`** *`(UserSecurity)`*: An instance of your `UserSecurity` subclass.

### `get()`

*core_lib.session.security_handler.SecurityHandler.get()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/session/security_handler.py){:target="_blank"}

Returns the registered `UserSecurity` instance. Raises `ValueError('SecurityHandler was not set')` if nothing was registered.

```python
def get() -> UserSecurity:
```

## RequireLogin Decorator

*core_lib.web_helpers.flask.require_login.RequireLogin* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/flask/require_login.py){:target="_blank"}

*core_lib.web_helpers.django.require_login.RequireLogin* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/django/require_login.py){:target="_blank"}

Guards a view with the registered `UserSecurity`, as described in [How a request is checked](#how-a-request-is-checked). There is one class per framework; import the one that matches yours.

```python
class RequireLogin(object):
    def __init__(self, policies=None):
```

**Arguments**

- **`policies`** *`(list)`*: Default `None` (treated as `[]`). Passed to your `secure_entry()` as `policies`.

Put `@HandleException()` directly under `@RequireLogin` (as in the example below). `@RequireLogin` catches an exception raised by the view, logs it and returns nothing, so the framework answers with its own HTML error page. With `@HandleException()` underneath, the view's errors become JSON error responses instead.

## UserAuthMiddleware

*core_lib.web_helpers.flask.user_auth_middleware.UserAuthMiddleware* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/flask/user_auth_middleware.py){:target="_blank"}

*core_lib.web_helpers.django.user_auth_middleware.UserAuthMiddleware* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/django/user_auth_middleware.py){:target="_blank"}

Optional. `@RequireLogin` checks the cookie but does not hand the user to your view. Add this middleware when a view needs to know who is logged in. On every request that carries the auth cookie it calls `token_to_session_object()` and stores the result:

- **Flask:** in `request.environ['user']`.
- **Django:** in `request.user`.

If there is no cookie, nothing is set. If the token is invalid or expired, the value is `None`. The middleware never blocks a request; that is `@RequireLogin`'s job.

The two versions are installed differently; see [Flask vs Django](#flask-vs-django).

## Example

A complete Flask setup: a session object, a `UserSecurity` subclass, startup registration, a protected view and a login view.

### 1. Define what a logged-in user looks like

```python
class SessionUser:
    def __init__(self, user_id: int, email: str, role: str):
        self.user_id = user_id
        self.email = email
        self.role = role   # for example 'admin', 'editor', 'viewer'
```

### 2. Subclass `UserSecurity` with your auth rules

`User` is your SQLAlchemy entity with `id`, `email` and `role` columns. The token payload uses its column names as keys.

```python
from http import HTTPStatus

from core_lib.session.user_security import UserSecurity
from core_lib.web_helpers.request_response_helpers import response_status

from your_core_lib.data_layers.data.db.entities.user import User


class AppSecurity(UserSecurity):

    def generate_session_data(self, user: dict) -> dict:
        # `user` is what you pass to generate_session_data_token() at login (step 4):
        # here, the dict your user service returns. The result becomes the token payload.
        return {
            User.id.key: user[User.id.key],
            User.email.key: user[User.email.key],
            User.role.key: user[User.role.key],
        }

    def from_session_data(self, session_data: dict) -> SessionUser:
        # `session_data` is the decoded token payload (JWT also adds an `exp` key).
        return SessionUser(session_data[User.id.key], session_data[User.email.key], session_data[User.role.key])

    def secure_entry(self, request, session_obj: SessionUser, policies: list):
        # Return None to let the request through to the view.
        # Return a response to block it: that response is sent and the view does not run.
        if session_obj is None:  # no cookie
            return response_status(HTTPStatus.UNAUTHORIZED)
        if policies and session_obj.role not in policies:  # logged in, but not allowed here
            return response_status(HTTPStatus.FORBIDDEN)
        return None
```

The values in `policies` must compare equal to `SessionUser.role`. Strings are used here. If your roles are an enum, store its value in the token (the payload must be JSON-serializable) and convert it back to the enum in `from_session_data()`.

### 3. Register at startup and protect views

Initialize `WebHelpersUtils` first so the `response_*` helpers know which framework's response object to build. `JWT_SECRET` is an environment variable holding your signing key.

```python
import os
from datetime import timedelta

from flask import Flask, request

from core_lib.session.jwt_token_handler import JWTTokenHandler
from core_lib.session.security_handler import SecurityHandler
from core_lib.web_helpers.decorators import HandleException
from core_lib.web_helpers.flask.require_login import RequireLogin
from core_lib.web_helpers.flask.user_auth_middleware import UserAuthMiddleware
from core_lib.web_helpers.request_response_helpers import response_json
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils

COOKIE_NAME = 'app_cookie'

WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)
token_handler = JWTTokenHandler(os.environ['JWT_SECRET'], timedelta(hours=1))
SecurityHandler.register(AppSecurity(COOKIE_NAME, token_handler))

app = Flask(__name__)
# Optional: decode the cookie on every request and put the user in request.environ['user'].
app.wsgi_app = UserAuthMiddleware(app.wsgi_app, cookie_name=COOKIE_NAME)


@app.route('/admin')
@RequireLogin(policies=['admin'])
@HandleException()
def admin_dashboard():
    session_user = request.environ['user']  # set by UserAuthMiddleware
    return response_json({'dashboard': 'admin data', 'viewer': session_user.email})
```

The decorator order matters: `@app.route` first, then `@RequireLogin`, then `@HandleException()`.

### 4. Issue tokens on login

Add the login view to the same file. `core_lib` is your `CoreLib` instance, and `core_lib.user.authenticate()` is a method of your own user service that returns the user as a dict, or `None` when the email or password is wrong.

```python
from http import HTTPStatus

from flask import request

from core_lib.web_helpers.request_response_helpers import request_body_dict, response_json, response_status


@app.route('/login', methods=['POST'])
@HandleException()
def login():
    body = request_body_dict(request)
    user = core_lib.user.authenticate(body['email'], body['password'])
    if not user:
        return response_status(HTTPStatus.UNAUTHORIZED)
    token = SecurityHandler.get().generate_session_data_token(user)
    response = response_json({'ok': True})
    response.set_cookie(COOKIE_NAME, token, httponly=True)  # add secure=True when served over HTTPS
    return response
```

### What happens

Run with Flask's test client, this app gives:

| Request | Response |
|---|---|
| `POST /login` with an admin's email and password | `200 {"ok": true}` and the `app_cookie` cookie |
| `GET /admin` with the cookie of admin `ada@example.com` | `200 {"dashboard": "admin data", "viewer": "ada@example.com"}` |
| `GET /admin` with a viewer's cookie | `403`, empty body; the view does not run |
| `GET /admin` with no cookie | `401`, empty body |
| `GET /admin` with an expired token | `401 {"message": "Unauthorized"}` |
| `GET /admin` with a cookie that is not a valid token | `500 {"error": "Internal Server Error"}` |
| `POST /login` with a wrong password | `401`, empty body |

---

## Flask vs Django

The classes have the same names in both frameworks, but they plug in differently.

| | Flask | Django |
|---|---|---|
| `RequireLogin` import | `core_lib.web_helpers.flask.require_login` | `core_lib.web_helpers.django.require_login` |
| Decorated view | takes no `request` argument; use `flask.request` | takes `request` as its first argument |
| `UserAuthMiddleware` import | `core_lib.web_helpers.flask.user_auth_middleware` | `core_lib.web_helpers.django.user_auth_middleware` |
| Installing the middleware | wrap the WSGI app: `app.wsgi_app = UserAuthMiddleware(app.wsgi_app, cookie_name=...)` | add its path to `MIDDLEWARE` in `settings.py` |
| Cookie the middleware reads | the `cookie_name` argument | the **`COOKIE_NAME` setting**, which you must define |
| Where the middleware puts the user | `request.environ['user']` | `request.user` |
| `WebHelpersUtils.init()` | `WebHelpersUtils.ServerType.FLASK` | `WebHelpersUtils.ServerType.DJANGO` |

`@RequireLogin` always reads the cookie named by your `UserSecurity`'s `cookie_name`. The middleware reads its own setting, so keep the two names the same.

### Django setup

The Django middleware reads the cookie name from `settings.COOKIE_NAME`. If that setting is missing, every request fails with `AttributeError: ... has no attribute 'COOKIE_NAME'`.

```python
# settings.py
COOKIE_NAME = 'app_cookie'   # the same name you give your UserSecurity

MIDDLEWARE = [
    # ... Django's own middleware ...
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # if you use django.contrib.auth
    'core_lib.web_helpers.django.user_auth_middleware.UserAuthMiddleware',
]
```

Django's `AuthenticationMiddleware` also sets `request.user`. If you use both, list Core-Lib's middleware **after** it, or Django's will replace your session object. When a request has no auth cookie, Core-Lib's middleware leaves `request.user` alone: it is Django's `AnonymousUser` if you use `django.contrib.auth`, and missing otherwise.

Register `UserSecurity` once at startup, for example in your app's `AppConfig.ready()`:

```python
# your_app/apps.py
import os
from datetime import timedelta

from django.apps import AppConfig
from django.conf import settings

from core_lib.session.jwt_token_handler import JWTTokenHandler
from core_lib.session.security_handler import SecurityHandler
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils


class YourAppConfig(AppConfig):
    name = 'your_app'

    def ready(self):
        from your_app.security import AppSecurity  # the class from step 2

        WebHelpersUtils.init(WebHelpersUtils.ServerType.DJANGO)
        token_handler = JWTTokenHandler(os.environ['JWT_SECRET'], timedelta(hours=1))
        SecurityHandler.register(AppSecurity(settings.COOKIE_NAME, token_handler))
```

Views take `request`, and the user is on `request.user`. The login view is the same as in step 4, except for its `request` argument and the cookie name:

```python
# your_app/views.py
from http import HTTPStatus

from django.conf import settings

from core_lib.session.security_handler import SecurityHandler
from core_lib.web_helpers.decorators import HandleException
from core_lib.web_helpers.django.require_login import RequireLogin
from core_lib.web_helpers.request_response_helpers import request_body_dict, response_json, response_status


@RequireLogin(policies=['admin'])
@HandleException()
def admin_dashboard(request):
    return response_json({'dashboard': 'admin data', 'viewer': request.user.email})


@HandleException()
def login(request):
    body = request_body_dict(request)
    user = core_lib.user.authenticate(body['email'], body['password'])
    if not user:
        return response_status(HTTPStatus.UNAUTHORIZED)
    token = SecurityHandler.get().generate_session_data_token(user)
    response = response_json({'ok': True})
    response.set_cookie(settings.COOKIE_NAME, token, httponly=True)
    return response
```

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="core_lib_listener.html">Previous</a></button>
    <button class="pageNext-btn"><a href="handle_exceptions.html">Next</a></button>
</div>
