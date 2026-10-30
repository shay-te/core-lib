---
name: core-lib-main
description: MANDATORY — load this skill BEFORE you add or change the main `<Name>CoreLib(CoreLib)` class of a *-core-lib (the composition root): wiring a service, DataAccess, connection, client or cache into `__init__`, registering a cache handler or observer, `get_or_reg`/`instantiate_config`, `install()`/`uninstall()`, the `<Name>CoreLibInstance` holder, or composing another CoreLib; do not write it from memory. The pieces it wires come from core-lib-entity/-data-access/-service/-connection/-job/-observer.
---

# The main class — the composition root

Every *-core-lib has exactly one `<Name>CoreLib(CoreLib)` in `<name>_core_lib/<name>_core_lib.py`.
Its `__init__` builds every connection, client, DataAccess and service **once**, from config, and
exposes the services. Routes, jobs, scripts and tests all call that one object. Nothing else in
the library builds infrastructure (§7; docs: *The CoreLib Class*, *Registry*, *Instantiate Config*).

## Canonical shape (§7)

```python
import inspect
import os

from omegaconf import DictConfig

from core_lib.alembic.alembic import Alembic
from core_lib.cache.cache_handler_ram import CacheHandlerRam
from core_lib.core_lib import CoreLib
from core_lib.helpers.config_instances import instantiate_config

from foo_core_lib.constants import FOO_CORE_LIB_CACHE
from foo_core_lib.data_layers.data_access.thing_data_access import ThingDataAccess
from foo_core_lib.data_layers.service.thing_service import ThingService


class FooCoreLib(CoreLib):
    def __init__(self, conf: DictConfig):
        super().__init__()                                                   # 1. always first
        self.config = conf

        if not CoreLib.cache_registry.get(FOO_CORE_LIB_CACHE):              # 2. guarded registrations
            CoreLib.cache_registry.register(FOO_CORE_LIB_CACHE, CacheHandlerRam())

        core_cfg = conf.core_lib
        db = CoreLib.connection_factory_registry.get_or_reg(core_cfg.data.sqlalchemy)   # 3. connections
        billing_client = instantiate_config(core_cfg.foo_core_lib.client.billing)       #    and clients

        self._thing_da = ThingDataAccess(db)                                 # 4. DataAccesses: private
        self.thing = ThingService(self._thing_da, billing_client)            # 5. services: public, singular

        self.load_jobs(core_cfg.foo_core_lib.jobs, {'thing_due': self})     # 6. jobs last (core-lib-job)

    @staticmethod
    def install(cfg: DictConfig):
        Alembic(os.path.dirname(inspect.getfile(FooCoreLib)), cfg).upgrade()

    @staticmethod
    def uninstall(cfg: DictConfig):
        Alembic(os.path.dirname(inspect.getfile(FooCoreLib)), cfg).downgrade()
```

The order is load-bearing: `super().__init__()` sets up the listener list `attach_listener()` and
`start_core_lib()` use; a service is built after every service it depends on; `load_jobs()` comes
last because a `startup` job runs the moment it is scheduled, before `__init__` returns.

## One CoreLib per process — guard every registration

These are **class attributes of `CoreLib`**, one per Python process, shared by every CoreLib in it:
`cache_registry`, `observer_registry`, `connection_factory_registry`, `handle_exception_middleware`
and the job `scheduler` (plus the `SecurityHandler` singleton on the web side).

- `register()` **raises `ValueError` on a duplicate key**, so building the class a second time
  (tests, a host composing several libs) fails unless every registration is guarded:
  `if not CoreLib.cache_registry.get(KEY): CoreLib.cache_registry.register(KEY, ...)`.
- `get()` with **no key** returns the default, or the **first** handler registered in the process.
  Always name the handler (`@Cache(handler_name=FOO_CORE_LIB_CACHE)`, `@Observe(observer_name=...)`),
  or a host that composes several libs silently uses another lib's.
- Two configs in one process do not give two separate apps: they share the cache, observers and
  scheduler. Different tiers are different deployments.

## Connections and clients — from config, never hard-coded

| Block | Build it with | Why |
|---|---|---|
| SQL (`core_lib.data.sqlalchemy`) | `CoreLib.connection_factory_registry.get_or_reg(block)` | one engine per process for every lib that names the same `_instance_key_`; Alembic reads this exact path (§3.1) |
| any block with `_instance_key_` | `get_or_reg(block)` — **never** `instantiate_config` | `instantiate_config` passes `_instance_key_` to the constructor, which rejects it (a `ValueError` caused by `unexpected keyword argument '_instance_key_'`); `get_or_reg` strips it |
| a client, provider or factory named by `_target_` | `instantiate_config(block)` (optionally with a base class: `instantiate_config(block, CacheHandler)`) | the class lives in YAML, so a test config swaps a fake in by changing `_target_` |

`instantiate_config` adds over Hydra's `instantiate`: a base-class check, `params` merged over the
YAML, `class_config_base_path` to find `_target_` under a sub-key, one `ValueError` naming the
config that failed, and `None` for an empty block.

## Public surface

- **Services are the API.** One public attribute per service, named after the class minus
  `Service`, snake_case, **singular**: `WorkspaceService` → `self.workspace` (§1). Never plural.
- **DataAccesses are private** (`self._thing_da`) or local variables. A public DataAccess leaks
  raw ORM rows and cache misses past the service's `@Cache`/`@ResultToDict`.
- **Read config by attribute and fail loud** — `conf.core_lib.foo_core_lib.limits.max_upload_bytes`,
  never `.get(..., default)` or `or {}` (Repo-specific context). Every key read exists in the yaml.
- Host extension hooks are explicit methods (`attach_foo_listener(...)`, `register_extractor(...)`);
  a host never reaches through the composition.

## The instance holder — build it once, call `start_core_lib()` once

The host's entry point builds the object once per process; everything else reads it back. This is
the file `core_lib generate` writes as `<name>_core_lib_instance.py`:

```python
from foo_core_lib.foo_core_lib import FooCoreLib


class FooCoreLibInstance(object):
    _app_instance = None

    @staticmethod
    def init(core_lib_cfg):
        if not FooCoreLibInstance._app_instance:
            FooCoreLibInstance._app_instance = FooCoreLib(core_lib_cfg)
            FooCoreLibInstance._app_instance.start_core_lib()   # fires on_core_lib_ready() once

    @staticmethod
    def get() -> FooCoreLib:
        return FooCoreLibInstance._app_instance
```

`start_core_lib()` raises `CoreLibInitException` if called twice on the same object. It does NOT
start jobs — `load_jobs()` already scheduled them in `__init__`. Each web worker process builds its
own instance; that is expected.

## Composing another CoreLib

Build it inside `__init__` with the **same** config (`self.doc_to_markdown = DocToMarkdownCoreLib(conf)`),
pass the piece your services need into them, and expose host hooks as pass-through methods. It shares
the process-wide registries, so it must guard its registrations too. If it needs a section of its own
config, provide that section inline in your yaml — never compose another repo's config group (§3.4).

## Rules to enforce

- `super().__init__()` first; registrations guarded; `load_jobs()` last (§7, §9).
- SQL through `get_or_reg(core_cfg.data.sqlalchemy)`; `_target_` blocks through `instantiate_config`;
  a block with `_instance_key_` only through `get_or_reg`.
- Services public and singular; DataAccesses private; nothing builds infrastructure outside `__init__`.
- `install()`/`uninstall()` exactly as above — the import is `core_lib.alembic.alembic` (§7, §11.1).
- The class has no business logic: it wires.

Pieces it wires: `core-lib-data-access`, `core-lib-service`, `core-lib-connection`, `core-lib-job`,
`core-lib-observer`. Bootstrap of a whole new lib: `core-lib-new`.
