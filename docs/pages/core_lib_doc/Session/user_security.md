---
id: user_security
title: User Security
sidebar: core_lib_doc_sidebar
permalink: user_security.html
folder: core_lib_doc
toc: false
---

Auth requirements differ per app — JWT tokens, session cookies, role-based access — but the request wiring is always the same: extract the token, decode it, validate it, decide whether to allow the request. `UserSecurity` is an abstract interface you implement once for your specific auth logic; everything else (cookie extraction, token decode, decorator wiring) is handled by Core-Lib.

> **Where it fits:** Web edge + Service. `UserSecurity` subclasses implement auth logic; `@RequireLogin` guards route handlers; `UserAuthMiddleware` plugs into the framework's request lifecycle.

> Unfamiliar with terms like "decorator", "session", or "WSGI"? See the [Glossary](/glossary.html).

## UserSecurity

*core_lib.session.user_security.UserSecurity* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/session/user_security.py#L6){:target="_blank"}

`UserSecurity` is an abstract class. Extend it and implement the abstract methods for your app's auth logic.

```python
class UserSecurity(ABC):
    def __init__(self, cookie_name: str, token_handler: TokenHandler):
```

**Arguments**

- **`cookie_name`** *`(str)`*: Name of the cookie in which the token is passed
- **`token_handler`** *`(TokenHandler)`*: Expects a `TokenHandler` class that implements the `encode` and `decode` functions.

>`UserSecurity` token handler uses the `JWTTokenHandler` in `Core-Lib` which handles the [jwt](https://jwt.io){:target="_blank"} tokens. 



## Functions

### secure_entry()

*core_lib.session.user_security.UserSecurity.secure_entry()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/session/user_security.py#L14){:target="_blank"}

Implement this method to decide whether a decoded session is allowed to enter. Use `policies` for role or permission checks supplied by the `RequireLogin` decorator.

```python
def secure_entry(self, request, session_obj, policies: list):
```

**Arguments**

- **`request`**: The received request object.
- **`session_obj`**: Decoded and formatted session data.
- **`policies`** *`(list)`*: List of policies that will be required for further authentication or authorization.

### from_session_data()

*core_lib.session.user_security.UserSecurity.from_session_data()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/session/user_security.py#L19){:target="_blank"}

Implement this method to convert decoded token data into the session object your app uses.

```python
def from_session_data(self, session_data: dict):
```

**Arguments**

- **`session_data`** *`(dict)`*: Decoded session data received from `_secure_entry()`.

### generate_session_data()

*core_lib.session.user_security.UserSecurity.generate_session_data()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/session/user_security.py#L23){:target="_blank"}

Implement this method to convert your user object into the dict that will be encoded into the session token.

```python
def generate_session_data(self, obj) -> dict:
```

**Arguments**

- **`obj`**: Data that must be structured and returned.

**Returns**

*`(dict)`*: Returns session data dictionary.


### generate_session_data_token()

*core_lib.session.user_security.UserSecurity.generate_session_data_token()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/session/user_security.py#L26){:target="_blank"}

Encodes the dict returned by `generate_session_data()` and returns the token.

```python
def generate_session_data_token(self, obj):
```

**Arguments**

- **`obj`**: The user object passed to `generate_session_data()`.

**Returns**

Returns encoded token.

### _secure_entry()

*core_lib.session.user_security.UserSecurity._secure_entry()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/session/user_security.py#L38){:target="_blank"}

Called by the `@RequireLogin` decorator. It reads the token from the request, converts it to a session object, then calls your `secure_entry()` implementation.

```python
def _secure_entry(self, request, policies):
```

**Arguments**

- **`request`**: Request object received by the decorator. It must contain the auth cookie.

- **`policies`**: List of policies that will be passed to `secure_entry()`

**Returns**

Returns whatever your `secure_entry()` implementation returns.


## SecurityHandler

*core_lib.session.security_handler.SecurityHandler* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/session/security_handler.py#L4){:target="_blank"}

A process-wide registry for your `UserSecurity` implementation. Register it once at startup; the `RequireLogin` decorator and any code that needs to issue tokens calls `SecurityHandler.get()` to reach it.

```python
class SecurityHandler(object):
```

### `register()`

*core_lib.session.security_handler.SecurityHandler.register()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/session/security_handler.py#L8){:target="_blank"}

Registers your `UserSecurity` implementation.

```python
def register(user_security: UserSecurity):
```

**Arguments**

- **`user_security`** *`(UserSecurity)`*: `UserSecurity` implemented class.

### `get()`

*core_lib.session.security_handler.SecurityHandler.get()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/session/security_handler.py#L14){:target="_blank"}

Returns the registered `UserSecurity` instance.

```python
def get() -> UserSecurity:
```

**Returns**

*`(UserSecurity)`*: Returns `UserSecurity` class object.


## RequireLogin Decorator

*core_lib.web_helpers.django.require_login.RequireLogin* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/django/require_login.py#L10){:target="_blank"}

This decorator runs authorization/authentication through the registered `UserSecurity` instance. It accepts `policies`, reads the request object using the matching Flask or Django integration, calls `_secure_entry()`, then returns that response.

```python
class RequireLogin(object):
    def __init__(self, policies=None):
```

**Arguments**

- **`policies`** *`(list)`*: List of policies that will be passed on to the `UserSecurity` functions.


## UserAuthMiddleware

*core_lib.web_helpers.django.user_auth_middleware.UserAuthMiddleware* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/django/user_auth_middleware.py#L7){:target="_blank"}

Configure this middleware in Django's `MIDDLEWARE` list. It checks for the configured cookie, converts the token into your session object, and assigns it to `request.user`.

```python
class UserAuthMiddleware(MiddlewareMixin):
```

## Example

A minimal end-to-end auth setup has three pieces: a session object, a `UserSecurity` subclass, and registration with `SecurityHandler`. After that, `@RequireLogin` on any view checks the cookie and enforces your policies.

### 1. Define what a logged-in user looks like

```python
class SessionUser:
    def __init__(self, id: int, email: str, role: str):
        self.id = id
        self.email = email
        self.role = role   # e.g. 'admin', 'editor', 'viewer'
```

### 2. Subclass `UserSecurity` with your auth rules

```python
from http import HTTPStatus
from core_lib.session.user_security import UserSecurity
from core_lib.session.jwt_token_handler import JWTTokenHandler
from core_lib.web_helpers.request_response_helpers import response_status


class AppSecurity(UserSecurity):
    def __init__(self, cookie_name, secret, expiration):
        super().__init__(cookie_name, JWTTokenHandler(secret, expiration))

    def from_session_data(self, data: dict) -> SessionUser:
        return SessionUser(data['id'], data['email'], data['role'])

    def generate_session_data(self, user) -> dict:
        return {'id': user['id'], 'email': user['email'], 'role': user['role']}

    def secure_entry(self, request, session: SessionUser, policies: list):
        # session is None when no cookie / invalid token — reject before touching .role
        if session and (not policies or session.role in policies):
            return response_status(HTTPStatus.OK)
        return response_status(HTTPStatus.UNAUTHORIZED)
```

### 3. Register at startup and protect views

The Flask version of `RequireLogin` reads from Flask's request context — your view takes no `request` parameter. The Django version takes `request` as usual. Use the matching import for your framework.

Before using any `response_*` helper, initialize `WebHelpersUtils` once at startup so the helpers know which framework's response object to build.

```python
# Flask app bootstrap
from datetime import timedelta
from core_lib.session.security_handler import SecurityHandler
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
from core_lib.web_helpers.flask.require_login import RequireLogin

WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)
SecurityHandler.register(AppSecurity('app_cookie', 'super-secret', timedelta(hours=1)))

@RequireLogin(policies=['admin'])
def admin_dashboard():
    ...
```

```python
# Django app bootstrap (e.g. apps.py ready() or settings)
from datetime import timedelta
from core_lib.session.security_handler import SecurityHandler
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
from core_lib.web_helpers.django.require_login import RequireLogin

WebHelpersUtils.init(WebHelpersUtils.ServerType.DJANGO)
SecurityHandler.register(AppSecurity('app_cookie', 'super-secret', timedelta(hours=1)))

@RequireLogin(policies=['admin'])
def admin_dashboard(request):
    ...
```

### 4. Issue tokens on login

```python
from core_lib.web_helpers.request_response_helpers import response_json, request_body_dict

def login(request):
    body = request_body_dict(request)
    user = core_lib.user.authenticate(body['email'], body['password'])
    token = SecurityHandler.get().generate_session_data_token(user)
    response = response_json({'ok': True})
    response.set_cookie('app_cookie', token)
    return response
```

That is the whole flow. Everything else — multi-role policies, status flags, custom token handlers — is added on top of these four pieces. `policies`, `SessionUser.role`, and the values you put in `generate_session_data` must all share the same type — strings here, but enums or ints work equally well as long as they match across the three.

---

## Flask vs Django

The API is identical for both frameworks — only the import path differs.

| Class | Flask import | Django import |
|---|---|---|
| `RequireLogin` | `core_lib.web_helpers.flask.require_login` | `core_lib.web_helpers.django.require_login` |
| `UserAuthMiddleware` | `core_lib.web_helpers.flask.user_auth_middleware` | `core_lib.web_helpers.django.user_auth_middleware` |

The Flask version of `RequireLogin` reads from Flask's `request` context, so the decorated view takes no `request` parameter. The Django version takes `request` as usual.

The Flask `UserAuthMiddleware` wraps the WSGI app directly:

```python
from flask import Flask
from core_lib.web_helpers.flask.user_auth_middleware import UserAuthMiddleware

app = Flask(__name__)
app.wsgi_app = UserAuthMiddleware(app.wsgi_app, cookie_name='app_cookie')
```

The Django version is registered in `MIDDLEWARE` in `settings.py`.

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/core_lib_listener.html">Previous</a></button>
    <button class="pageNext-btn"><a href="/handle_exceptions.html">Next</a></button>
</div>
