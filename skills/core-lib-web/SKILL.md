---
name: core-lib-web
description: MANDATORY — load this skill BEFORE you write or change web routes/views that call a CoreLib, or use core-lib's web helpers — `WebHelpersUtils`, `response_*`/`generate_response`, `@HandleException`/`handle_exception`, `CoreLib.handle_exception_middleware`, `MiddlewareChain`, `UserSecurity`/`SecurityHandler`/`JWTTokenHandler`, `@RequireLogin`, `UserAuthMiddleware`; do not write it from memory. These live at the host's web edge; a *-core-lib's services never import them.
---

# The web edge: calling a CoreLib from Flask or Django

Routes are the only code that knows the web framework. They read the request, call a service on
the process's one CoreLib, and return the result. Core-Lib's helpers make that the same for Flask
and Django (docs: *Web Helpers*, *HandleException Decorator*, *Middleware*, *User Security*).

## ⛔ The boundary

- **A *-core-lib never imports a web helper, `flask` or `django`** — not in a service, a
  DataAccess or an entity. Services raise `StatusCodeException` (core-lib-error-handling) and return
  dicts; the web edge turns those into responses. A service that reads `request` or builds a
  `Response` cannot be called from a job, a script or a test.
- **The helpers support Flask and Django only.** On FastAPI (or anything else) call the CoreLib from
  your routes directly and use that framework's own error and auth handling.
- **The host installs `core-lib[flask]` or `core-lib[django]`.** A plain `core-lib` has neither
  framework nor PyJWT, which `@HandleException` imports.
- **Build the CoreLib once per process, never per request** (core-lib-main): an instance holder
  initialised at startup, read back by every route.

## 1. Initialise once, at startup

```python
from core_lib.web_helpers.web_helpers_utils import WebHelpersUtils

WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)    # or DJANGO; once per process
```

Every `response_*` helper and `@HandleException` read this setting. Without it, an exception in a
decorated view escapes as `ValueError('WebHelpersUtils never initialized')` instead of a 500. (The
old module name `web_helprs_utils` still imports but is deprecated.)

## 2. Views: call the service, return its dict

```python
from http import HTTPStatus

from flask import Flask, request

from core_lib.error_handling.status_code_exception import StatusCodeException
from core_lib.web_helpers.decorators import HandleException
from core_lib.web_helpers.request_response_helpers import request_body_dict, response_json

app = Flask(__name__)


@app.post('/things')
@HandleException()
def create_thing():
    thing = FooCoreLibInstance.get().thing.create(request_body_dict(request))
    return response_json(thing, HTTPStatus.CREATED)


@app.get('/things/<int:thing_id>')
@HandleException()
def get_thing(thing_id: int):
    thing = FooCoreLibInstance.get().thing.get(thing_id)
    if thing is None:
        raise StatusCodeException(HTTPStatus.NOT_FOUND, f'no thing {thing_id}')   # -> 404
    return response_json(thing)
```

Response helpers (all return a Flask `Response` or Django `HttpResponse`): `response_status`,
`response_ok`, `response_message`, `response_json`, `response_error`, `response_download_content`,
and `generate_response(data, status, media_type, headers)` for another content type or extra headers.

## 3. `@HandleException()` — exceptions become statuses

| Raised in the view or anything it calls | Response |
|---|---|
| `StatusCodeException(status, ...)` | that status; body `{"message": "<reason phrase>"}`, or `{"error": ...}` for 500+ |
| `jwt.ExpiredSignatureError` | `401 {"message": "Unauthorized"}` |
| Flask `abort(code)` / Werkzeug `HTTPException`; Django `Http404`, `PermissionDenied`, `BadRequest`/`SuspiciousOperation` | its own code; 404, 403, 400 — same body shape |
| anything else, `AssertionError` included | `500 {"error": "Internal Server Error"}` |

- The exception's **message is logged, never sent**: the body carries only the reason phrase. To
  send your own text, catch it in the view and return `response_json`/`response_error`.
- Order: `@app.route` → `@RequireLogin` → `@HandleException()` → the view. Without
  `@HandleException()` under `@RequireLogin`, a view error is swallowed and the framework answers
  with its own HTML error page.
- Process-wide error reporting (Sentry, audit, alerts) goes on `CoreLib.handle_exception_middleware`,
  a `MiddlewareChain` that runs on every exception the decorator catches. Add your `Middleware` once
  at startup; its context has `exc`, `func`, `request` (always `None` on Django) and `stacktrace`.
  A middleware that raises stops the ones after it but never changes the response.

## 4. Login: `UserSecurity` + `@RequireLogin`

1. Subclass `UserSecurity(cookie_name, token_handler)` and implement `generate_session_data(user)`
   (the token payload — small, JSON-serializable, keyed by `Entity.col.key`),
   `from_session_data(payload)` (payload → your session object) and
   `secure_entry(request, session_obj, policies)`: **return `None` to let the view run**; return a
   response (e.g. `response_status(HTTPStatus.FORBIDDEN)`) to block it. Any response object blocks,
   even a 200.
2. Register once at startup: `SecurityHandler.register(AppSecurity(COOKIE_NAME, JWTTokenHandler(secret, timedelta(hours=1))))`.
   A second `register()` in the process raises `ValueError`. Load the secret from the environment;
   use 32+ bytes for HS256.
3. Guard views with `@RequireLogin(policies=[...])` — import the Flask or the Django class.
   `session_obj` is `None` without a cookie; an expired token answers 401 and an undecodable one 500
   before `secure_entry` runs.
4. At login: `token = SecurityHandler.get().generate_session_data_token(user)` and set it as an
   `httponly` cookie (`secure=True` over HTTPS). `JWTTokenHandler` adds a UTC `exp` claim and does
   not change your dict.
5. Optional `UserAuthMiddleware` puts the decoded session object on `request.environ['user']`
   (Flask; wrap `app.wsgi_app`) or `request.user` (Django; add to `MIDDLEWARE`, and define
   `settings.COOKIE_NAME` — without it Django refuses to start with `ImproperlyConfigured`). It never
   blocks a request.

Django: views take `request` first, `CsrfViewMiddleware` rejects a `POST /login` without a CSRF
token (send it, or `@csrf_exempt` deliberately), and list Core-Lib's middleware after Django's
`AuthenticationMiddleware`.

## Testing

Use the framework's test client against the real CoreLib built from the test config. Assert both
directions for every guarded view: the view **runs** for an allowed user (record that it ran — a
`secure_entry` that answers 200 instead of `None` passes status-only tests while the view never
runs) and does **not** run for a rejected one.

## Rules to enforce

- Web helpers, `flask` and `django` appear only in the host's web layer, never inside a *-core-lib.
- `WebHelpersUtils.init()`, `SecurityHandler.register()` and middleware registration run once per
  process, at startup.
- Every view is `@HandleException()`-decorated (directly under `@RequireLogin` when guarded);
  services signal errors with `StatusCodeException`, never framework exceptions.
- `secure_entry` returns `None` to allow.
