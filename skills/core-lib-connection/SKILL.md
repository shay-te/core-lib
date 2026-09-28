---
name: core-lib-connection
description: MANDATORY — load this skill BEFORE you add or change an external client, provider, API or SDK integration, HTTP client, connection factory, or any wrapper around a third-party service (LLM, object storage/S3, payment gateway) in a *-core-lib; do not write it from memory. Creates a ConnectionFactory that builds the SDK client once (fetch→validate→use, lazy import) plus a Connection with typed errors.
---

# Create a non-DB backend (the `connections/` pattern)

An outbound backend (object storage, an external API) is **three pieces**,
mirroring the DB stack. Files are named after the **backend**, with no lib
prefix (`storage_connection_factory.py`, not `foo_storage_...`). §10.

## The three pieces

**1. `connections/storage_connection_factory.py`** — `class
StorageConnectionFactory(ConnectionFactory)`. Validates **every** required
config key in `__init__` (this validation layer is the one sanctioned place
that may read with `config.get(...)`, because its whole job is to raise a
better error per missing key). The heavy SDK import is **lazy** — `import
boto3` is the first line *inside* the `_build_client` staticmethod, never at
module top, so the SDK stays an optional extra.

**2. `connections/storage_connection.py`** — **lifecycle only.** `__enter__`
returns the raw client; `__exit__` does nothing. **No verbs here.**

**3. `data_layers/data_access/storage_data_access.py`** — `class
StorageDataAccess(DataAccess)` owns **all** the verbs (`put`, `get`, `delete`,
`exists`, `list`, …).

```python
# connections/storage_connection_factory.py
class StorageConnectionFactory(ConnectionFactory):
    def __init__(self, config):
        provider = config.get('provider')          # sanctioned .get: validation layer
        bucket = config.get('bucket')
        if not provider:
            raise FooConfigError('storage.provider is required')
        if not bucket:
            raise FooConfigError('storage.bucket is required')
        self._client = self._build_client(provider, bucket)

    @staticmethod
    def _build_client(provider, bucket):
        import boto3                                # LAZY — never at module top
        return boto3.client('s3', ...)

    def get(self) -> StorageConnection:
        return StorageConnection(self._client)
```

## Composition root wiring — name the variable what it IS

```python
storage_data_access = StorageDataAccess(StorageConnectionFactory(storage_cfg))
```

Not `storage = StorageDataAccess(...)` — vague names for composed parts were
rejected in review (§0).

## Rules to enforce (§10)

- **Three pieces, that split exactly** — factory (config + client), connection
  (lifecycle only, no verbs), DataAccess (all verbs).
- **Lazy SDK import inside `_build_client`**; the SDK ships as an optional
  extra, never in `requirements.txt` (§14).
- **Validate every required key in the factory** and raise the lib's own typed
  error; callers never import the SDK's exception hierarchy.
- **The keys you read are library-owned and generic — never host-specific.**
  This is the agnosticism rule at the config boundary, and the factory is where
  it breaks. A core-lib NEVER reads a host's env var or a host-prefixed config
  key: it reads its own generic name, or better, takes the value as a
  constructor param. The host owns its config and **bridges** it — passing the
  value in, or exporting it under the generic name this library reads. Same for
  any product-specific text (endpoints, bucket names, prompts, operator
  messages): injected by the caller with a safe neutral default, never
  hardcoded here. Litmus: could a stranger configure this package without ever
  learning what application it came from? See "this library is AGNOSTIC" in
  `AGENTS.md`.
- **Provider quirks are absorbed in the factory** (e.g. `provider: minio` +
  `addressing_style: auto` → `path`). Ship `docker-compose-dev.yaml` with the
  real local backend rather than faking it in tests.
- Registries stay in-memory — re-register on process boot (§10).
