---
name: core-lib-client
description: MANDATORY — load this skill BEFORE you add or change a client for an external HTTP API in a *-core-lib (a REST/JSON service, an OAuth endpoint, any provider the lib reaches over HTTP); do not write it from memory. Builds it in `<lib>/client/` on core-lib's `ClientBase` (one class per base URL, an abstract client when several providers share one API), tested by faking only `ClientBase.session`. An SDK that owns its own connection (boto3/S3, a database driver) is core-lib-connection instead.
---

# Build an HTTP API client (the `client/` pattern)

`core_lib.client.client_base.ClientBase` is core-lib's HTTP client: it holds one
`base_url`, a `requests.Session`, and optional default headers / timeout / auth, and
exposes the verbs `_get` / `_post` / `_put` / `_delete(path, **kwargs)` (the path is
joined to `base_url`; the kwargs go to `requests`). Every client a lib uses to talk HTTP
is a `ClientBase` subclass in `<lib>/client/`.

## Which pattern?

| The backend is reached… | Pattern |
|---|---|
| over HTTP that the lib speaks itself (REST/JSON, OAuth, form posts) | **`client/` on `ClientBase`** — this skill |
| through an SDK that owns its connection (boto3/S3, a DB driver, a workflow engine) | `connections/` — `core-lib-connection` |

## Layout

```
foo_core_lib/
  client/
    __init__.py
    calendar_client.py            # CalendarClient(ClientBase, ABC): the API every provider shares
    acme_calendar_client.py       # AcmeCalendarClient(CalendarClient): one provider
    acme_oauth_client.py          # AcmeOAuthClient(ClientBase): the provider's second host
    acme_response_helper.py       # module functions reading the provider's answers (optional)
```

- **One class per file, named after the service + `Client`** (`AcmeCalendarClient` in
  `acme_calendar_client.py`).
- **One client per base URL.** `ClientBase` builds every URL from ONE `base_url`; a provider
  with two hosts (an API host and an OAuth host) is two clients, the second composed into
  the first through its constructor — never an absolute URL smuggled into a path.
- **Several providers behind one API** get an abstract base,
  `class XClient(ClientBase, ABC)`, declaring with `@abstractmethod` the method names and
  meanings every provider implements. Services depend on `XClient` only; the composition
  root builds a `{ProviderEnum: client}` map and a row's provider column picks the client.
- Clients live outside `data_layers/`: they do HTTP and nothing else — no DataAccess, no
  session, no service import. Services call clients; clients never call services.

## The shape

```python
from core_lib.client.client_base import ClientBase

ACME_CALENDAR_API_URL = 'https://api.acme.example/calendar/v1'
REQUEST_TIMEOUT_SECONDS = 15


class AcmeCalendarClient(CalendarClient):
    def __init__(self, acme_oauth_client: AcmeOAuthClient, calendar_name: str):
        # 1. validate every value first — a plain ValueError naming the KEY, never the value
        if not calendar_name or not isinstance(calendar_name, str):
            raise ValueError('foo_core_lib.calendar_name is required')
        if not isinstance(acme_oauth_client, AcmeOAuthClient):
            raise ValueError('an AcmeOAuthClient is required')
        # 2. then the base
        CalendarClient.__init__(self, ACME_CALENDAR_API_URL)
        self.set_timeout(REQUEST_TIMEOUT_SECONDS)
        self._acme_oauth_client = acme_oauth_client
        self._calendar_name = calendar_name

    def create_calendar(self, connection: FooClientConnection) -> str:
        response = acme_response_helper.send(
            'create_calendar', self._post, '/calendars',
            headers={'Authorization': f'Bearer {self._acme_oauth_client.access_token(...)}'},
            json={'name': self._calendar_name},
        )
        body = acme_response_helper.success_body(response, 'create_calendar')
        # 1. fetch
        calendar_id = body.get('id')
        # 2. validate
        if not calendar_id or not isinstance(calendar_id, str):
            raise FooProviderError('acme create_calendar returned no calendar id')
        # 3. use
        return calendar_id
```

Composition root — the config is read THERE and passed in; a client never reads config:

```python
acme_oauth_client = AcmeOAuthClient(foo_config.acme.client_id, foo_config.acme.client_secret)
acme_calendar_client = AcmeCalendarClient(acme_oauth_client, foo_config.calendar_name)
self._calendar_clients = {CalendarProvider.ACME: acme_calendar_client}
```

## Rules

- **Every request goes through the `ClientBase` verbs** (`self._post(path, ...)`) — never
  `requests.post(...)`, a second `requests.Session`, or `self.session.request(...)` with a
  hand-built URL. The base owns the session, URL joining, timeout and default headers.
- **Always set a timeout** (`self.set_timeout(...)` in `__init__`): `ClientBase` has none by
  default, and `requests` then waits forever.
- **Auth:** per-request credentials (a bearer token that changes) go in `headers=` on the
  call; static credentials use `set_headers` / `set_auth` once in `__init__`.
- **Network errors become the lib's own error.** Wrap the verb so a
  `requests.RequestException` is re-raised as the lib's provider error (a
  `StatusCodeException` subclass, typically 502), named by exception CLASS only and raised
  `from None` — the transport exception can quote URLs and headers.
- **Read every answer fetch → validate → use** (G4): status first, then the JSON body, then
  each field into a named local, validated before use. A 200 with an unusable body is a
  provider error, not a crash.
- **Error messages carry status codes and the provider's machine-readable error codes
  only** — never a token, a credential, or the provider's human message (it may quote user
  data). Keep secrets out of `repr` (`field(repr=False)` on data types holding them).
- **Public methods return data types** (`data_layers/data/data_types/`) or plain values —
  never a raw `requests.Response`.
- **Constructor params, validated, never config reads** — the composition root reads the
  lib's own generic config keys and passes values in; product wording (names, descriptions)
  is injected (the agnosticism rule).
- **Provider quirks stay in the provider's client** (status codes that mean success, error
  shapes); the abstract client's contract is what services rely on.

## Testing

- **The HTTP boundary is `client.session`** — the one thing a test replaces. Set it to a
  `requests.Session` subclass that overrides `request(method, url, **kwargs)` to record the
  call and answer from a scripted queue of real `requests.Response` objects (or raise a
  scripted `requests.RequestException`), failing on an unscripted call. Every `ClientBase`
  verb routes through `session.request`, so this sees them all — no network, and no
  `mock.patch` of the client's own methods.
- **Client unit files** (`test_<provider>_<service>_client_<area>.py`, one `TestCase`
  each) build the client directly — the sanctioned "client adapter" exception (AGENTS
  §13.3) — and assert the exact method, URL, query params, body and auth header sent, plus
  every failure mapping: HTTP error status, network error, unusable body.
- **Service suites** swap the provider client through a seam owned by
  `tests/helpers/utils.py` (`use_<x>_client` context manager) for a fake SUBCLASS of the
  abstract client, so the fake keeps the real signatures. At least one flow test drives the
  composed lib through the REAL client over the recording session.
- A construction test asserts the client is a `ClientBase` on the expected `base_url` with a
  timeout, and that every required value is enforced.
