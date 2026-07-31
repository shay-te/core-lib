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

from my_core_lib.data_layers.data.db.entities.widget import Widget
from my_core_lib.data_layers.data_access.widget_data_access import WidgetDataAccess

CACHE_KEY_WIDGET = 'widget_{widget_id}'


class WidgetService(Service):
    def __init__(self, widget_data_access: WidgetDataAccess):
        self._widget_data_access = widget_data_access

    @Cache(CACHE_KEY_WIDGET)          # @Cache OUTSIDE @ResultToDict
    @ResultToDict()
    def get(self, widget_id: int):
        return self._widget_data_access.get(widget_id)

    @DuplicateErrorHandler()          # outermost; only if entity has UniqueConstraint
    @ResultToDict()
    def create(self, data: dict):
        return self._widget_data_access.create(data)

    @Cache(CACHE_KEY_WIDGET, invalidate=True)   # write-through DA → evict same key
    @ResultToDict()
    def update(self, widget_id: int, data: dict):
        return self._widget_data_access.update(widget_id, data)

    def set_status(self, widget_id: int, status: Widget.Status):
        if not isinstance(status, Widget.Status):     # enum at the boundary
            raise ValueError('status must be a Widget.Status member')
        return self.update(widget_id, {Widget.status.key: status})
```

## Decorator order (always)

`@DuplicateErrorHandler()` (outermost) → `@Cache(...)` → `@ResultToDict()`
(innermost). Cache handlers only accept JSON-serializable values, so the row
must already be a dict when it reaches the cache; a cached getter therefore
returns a **dict** — internal consumers read `row[Widget.col.key]`, not
`.attr`.

## Cache decisions

- **Cache only cross-service hot paths** (service A asks service B the same
  question every request). Host-app PK-by-id reads stay uncached — record the
  "why not" in the service-class docstring (§4.4).
- Key template names every parameter the value depends on; templates are
  module-level constants (§4.5).
- Methods that write a row directly through the DA carry
  `@Cache(SAME_KEY, invalidate=True)`. Orchestrators that write only via other
  service methods need no decorator.
- `create` never evicts (misses aren't cached). Write-then-return-the-row must
  evict first, then re-read through the cached getter.
- `list`/`search`/`all` stay uncached (unbounded key space).

## Rules to enforce (from AGENTS.md)

- **Public vs private** — `_`-prefixed internals are not called from outside
  (§4.1).
- **Enums cross the boundary as enums, never raw ints** (§4.2); plain
  `enum.Enum`.
- **Unique-constraint races** → `@DuplicateErrorHandler()`, positive
  `if existing: update else: create`, never `try/except IntegrityError` (§4.3).
- **State transitions** (stateful entities) write a history row + an outbox row
  in addition to firing the observer event; pass raw enum/datetime values to
  history `create` (§4.6).
- **Invalidate caches on every mutation**, before the observer fan-out (§4.7).

Wire the Service into the main class with `core-lib-main`.
