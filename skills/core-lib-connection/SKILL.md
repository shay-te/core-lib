---
name: core-lib-connection
description: MANDATORY — load this skill BEFORE you add or change an external client, provider, API or SDK integration, HTTP client, connection factory, or any wrapper around a third-party service (LLM, object storage/S3, payment gateway) in a *-core-lib; do not write it from memory. Creates a ConnectionFactory that builds the SDK client once (fetch→validate→use, lazy import) plus a Connection with typed errors.
---

# Create a core-lib Connection (outbound integration)

Outbound integrations follow one shape, the same for every backend present or
future: a **factory** that builds the shared SDK client once, and a
**connection** that exposes the per-call surface.

## Steps

1. Create `<name>_core_lib/connections/<backend>_connection_factory.py` and
   `<backend>_connection.py`.
2. In the factory `__init__`, read config with **fetch → validate → use** and
   build the SDK client once via `_build_client` (lazy SDK import inside it).
3. Expose `get()` returning a fresh `Connection`.
4. Define a small set of typed errors; wrap SDK exceptions in them.

## Canonical template

```python
# my_core_lib/connections/foo_connection_factory.py
from core_lib.connection.connection_factory import ConnectionFactory

from my_core_lib.connections.foo_connection import FooConnection
from my_core_lib.error_handling.foo_errors import FooConfigError


class FooConnectionFactory(ConnectionFactory):
    def __init__(self, config):
        # 1. fetch
        api_key = config.get('api_key')
        endpoint = config.get('endpoint')
        injected_client = config.get('client')   # tests inject a fake here
        # 2. validate
        if not api_key:
            raise FooConfigError('api_key is required')
        if not endpoint:
            raise FooConfigError('endpoint is required')
        # 3. use
        self._client = injected_client or self._build_client(api_key, endpoint)

    def _build_client(self, api_key, endpoint):
        import foo_sdk                       # lazy import — only when actually building
        return foo_sdk.Client(api_key=api_key, base_url=endpoint)

    def get(self) -> FooConnection:
        return FooConnection(self._client)
```

```python
# my_core_lib/connections/foo_connection.py
from my_core_lib.error_handling.foo_errors import FooProviderError


class FooConnection:
    def __init__(self, client):
        self._client = client

    def do_thing(self, payload):
        try:
            raw = self._client.call(payload)
        except Exception as exc:            # wrap SDK errors in OUR typed error
            raise FooProviderError(str(exc)) from exc
        # fetch → validate → use when reading fields off `raw`
        result = getattr(raw, 'result', None)
        if result is None:
            raise FooProviderError('response missing result')
        return result

    def close(self):
        self._client.close()
```

## Rules to enforce (from AGENTS.md)

- **Connection-factory shape only** — factory builds the client once in
  `__init__`; `get()` returns a fresh connection. Don't add a parallel
  provider ABC with a different method surface (§5.1).
- **Lazy SDK import inside `_build_client`** so a one-backend install doesn't
  import the others; tests inject a fake client through config (§5.2).
- **fetch → validate → use** for both config reads and SDK-response parsing;
  no inline defaults, no aliases, no scattered `.get`/`getattr` in
  loops/returns (§1.1).
- **Typed errors, not stringly-checked** — wrap SDK exceptions in the lib's own
  error classes; callers never import the SDK's exception hierarchy (§5.3).
- **Dependencies**: depend on `core-lib`; put optional/heavy backend SDKs in
  `extras_require`, not `requirements.txt` (§5.4).
- **Registries are in-memory** — re-register on boot, no DB-backed persistence
  inside the library (§5.5).
