---
name: core-lib-service
description: MANDATORY — load this skill BEFORE you add or change a Service, business-logic layer, public core-lib method or API, caching or cache invalidation, unique-constraint (409) handling, or state-transition/observer logic in a *-core-lib; do not write it from memory. Creates a Service over a DataAccess with @Cache/@ResultToDict/@DuplicateErrorHandler and history+outbox. Raw queries go in core-lib-data-access.
---

# Create a core-lib Service (business logic + public API)

The Service layer owns business logic, caching, and transformation, and is the
library's **public API surface**. Callers outside the lib go through
`core_lib.some_service.some_method(...)` — never into a DataAccess directly.

## Steps

1. Confirm the DataAccess exists (use `core-lib-data-access` first).
2. Create `data_layers/service/<entity>_service.py` extending `Service`.
3. Wrap reads/writes with decorators in the right order.
4. Add caching only where the win is real (cross-service hot paths).
5. Type enum parameters as the enum and validate with an explicit raise.

## Canonical template

```python
from core_lib.data_layers.service.service import Service
from core_lib.data_transform.result_to_dict import ResultToDict
from core_lib.cache.cache_decorator import Cache
from core_lib.error_handling.duplicate_error_decorator import DuplicateErrorHandler

from core_lib.error_handling.status_code_exception import StatusCodeException

from my_core_lib.constants import FOO_CORE_LIB_CACHE
from my_core_lib.data_layers.data.db.entities.widget import Widget
from my_core_lib.data_layers.data_access.widget_data_access import WidgetDataAccess

CACHE_KEY_WIDGET = 'foo_widget_{widget_id}'   # '<lib>_<entity>_{param}' (§1)


class WidgetService(Service):
    def __init__(self, widget_data_access: WidgetDataAccess):
        self._widget_da = widget_data_access

    @Cache(CACHE_KEY_WIDGET, handler_name=FOO_CORE_LIB_CACHE)   # read: cache outermost
    @ResultToDict()                                             # dict conversion inside
    def get(self, widget_id: int):
        try:
            return self._widget_da.get(widget_id)
        except StatusCodeException:
            return None               # service swallows the DA's 404 into None

    @ResultToDict()                   # create: dict out; 409 mapping UNDER it
    @DuplicateErrorHandler()
    def create(self, data: dict):
        return self._widget_da.create(data)

    @Cache(CACHE_KEY_WIDGET, handler_name=FOO_CORE_LIB_CACHE, invalidate=True)  # writes evict
    def update(self, widget_id: int, data: dict):
        return self._widget_da.update(widget_id, data)

    def set_status(self, widget_id: int, status: Widget.Status):
        if not isinstance(status, Widget.Status):     # enum at the boundary
            raise ValueError('status must be a Widget.Status member')
        return self.update(widget_id, {Widget.status.key: status})
```

## Decorator order (always)

Copy these exactly (§6) — they are **not** one uniform order:

- **read:** `@Cache(KEY, handler_name=FOO_CORE_LIB_CACHE)` outermost →
  `@ResultToDict()` inside. Cache handlers only accept JSON-serializable
  values, so the row must already be a dict when it reaches the cache; a cached
  getter therefore returns a **dict** — consumers read `row[Widget.col.key]`,
  not `.attr`.
- **create:** `@ResultToDict()` outermost → `@DuplicateErrorHandler()` **under**
  it (the 409 mapping sits below the dict conversion).
- **write/evict:** `@Cache(KEY, handler_name=..., invalidate=True)` — no
  `@ResultToDict()`.
- **list:** `@ResultToDict()` only — never cached.

Always pass `handler_name=FOO_CORE_LIB_CACHE` (from `constants.py`).

## Cache decisions

- **Cache only cross-service hot paths** (service A asks service B the same
  question every request). Host-app PK-by-id reads stay uncached — record the
  "why not" in the service-class docstring (§6).
- Key template names every parameter the value depends on; templates are
  module-level constants (§6).
- Methods that write a row directly through the DA carry
  `@Cache(SAME_KEY, invalidate=True)`. Orchestrators that write only via other
  service methods need no decorator.
- `create` never evicts (misses aren't cached). Write-then-return-the-row must
  evict first, then re-read through the cached getter.
- `list`/`search`/`all` stay uncached (unbounded key space).

## Rules to enforce (from AGENTS.md)

- **Public vs private** — `_`-prefixed internals are not called from outside
  (§6).
- **Enums cross the boundary as enums, never raw ints** (§6); plain
  `enum.Enum`.
- **Unique-constraint races** → `@DuplicateErrorHandler()`, positive
  `if existing: update else: create`, never `try/except IntegrityError` (§6).
- **State transitions** (stateful entities) write a history row + an outbox row
  in addition to firing the observer event; pass raw enum/datetime values to
  history `create` (§A4).
- **Invalidate caches on every mutation**, before the observer fan-out (§6).

Wire the Service into the main class with `core-lib-main`.
