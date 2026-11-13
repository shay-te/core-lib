---
name: core-lib-service
description: MANDATORY — load this skill BEFORE you add or change a Service, business-logic layer, public core-lib method or API, caching or cache invalidation, unique-constraint (409) handling, or state-transition/observer logic in a *-core-lib; do not write it from memory. Creates a Service over a DataAccess with @Cache/@ResultToDict/@DuplicateErrorHandler and history+outbox. Raw queries go in core-lib-data-access.
---

# Create a core-lib Service (business logic + public API)

The Service layer owns business logic, caching, and transformation, and is the
library's **public API surface**. Callers outside the lib go through
`core_lib.some_service.some_method(...)` — never into a DataAccess directly.

## ⛔ Two filenames, and only two: `*_service.py` and `*_helper.py`

`ls data_layers/service/*.py` must show nothing else (bar `__init__.py`).
Opening the folder should tell you what each module is from the name alone.

| suffix | what it is |
|---|---|
| `thing_service.py` | a `Service` subclass — holds DataAccesses, decorated, public surface |
| `thing_helper.py` | a pure engine/helper — module-level functions, no DataAccess, no I/O, called BY a service |

A bare noun (`comparer.py`, `validator.py`, `definition_loader.py`) says which
of the two it is only after you open it. **Append the suffix to the WHOLE
name** — `definition_loader_helper.py`, not `definition_helper.py`: a
convention applied to two of three files is not a convention, and shortening
one to read better loses what the module is.

Some files should leave the folder instead of being renamed:

- a `@dataclass` → `data_layers/data/data_types/` (§4.1), or `error_handling/`
  if it is error-shaped (§4.2)
- a helper other LIBS would want → check `core_lib` first (`core-lib-reuse`)
- a helper a **DataAccess** also needs → the library root
  (`foo_core_lib/helpers.py`); importing it from `service/` inverts the layers
- two or three private derivations used by ONE service → leave them as
  module-level `_private` functions at the bottom of that service file. A
  `_helper.py` is for a body of logic with its own name.

Import a helper module qualified — `definition_loader_helper.scale(...)`, not
`from ... import scale` — the bare names collide with the local variables these
functions get assigned to.

## Steps

1. Confirm the DataAccess exists (use `core-lib-data-access` first).
2. Create `data_layers/service/<entity>_service.py` extending `Service`.
3. Wrap reads/writes with decorators in the right order.
4. Cache every read whose key bounds its result, and clear it on every write (see "Cache decisions").
5. Type enum parameters as the enum and take the member as given: no conversion
   from an int, no check of its own — the DataAccess's `RuleValidator` refuses a
   wrong value.
6. Any pure logic that grew its own name goes in `<name>_helper.py` beside it.

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

    def set_status(self, widget_id: int, status: Widget.Status):   # the member, never its int
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
- **list:** a per-tenant or per-parent list is a read (`@Cache` outermost); a paged or open-ended search is `@ResultToDict()` only.

Always pass `handler_name=FOO_CORE_LIB_CACHE` (from `constants.py`).

## Cache decisions

- **Cache every read whose key bounds its result (operator rule, §6)**: a by-id
  `get`, a per-tenant or per-parent list. Only a paged read or one keyed by an
  open-ended filter stays uncached.
- **Every write the library makes clears every key it changes, for every tenant
  or parent it reaches** (a row listed under several tenants clears each one's
  list), through one invalidation method its writers share. Data changed by hand
  in the database is cleared by hand by the operator: never a reason to leave a
  read uncached, and never assume a write path exists for it.
- **The cache is JSON: a dict's int keys come back as strings.** Cache the rows
  (a private `@Cache` + `@ResultToDict` read) and build the `{int id: ...}` dict
  after the cache.
- Key template names every parameter the value depends on; templates are
  module-level constants (§6).
- Methods that write a row directly through the DA carry
  `@Cache(SAME_KEY, invalidate=True)`. Orchestrators that write only via other
  service methods need no decorator.
- `create` never evicts (misses aren't cached). Write-then-return-the-row must
  evict first, then re-read through the cached getter.
- A paged `list` / free `search` stays uncached (unbounded key space).

## Rules to enforce (from AGENTS.md)

- **Extends `Service`** — every class in this folder. And the corollary: if a
  module here is not a Service, it does not belong in `service/`. That folder
  is a layer, not somewhere to park a helper.

- **Public vs private** — `_`-prefixed internals are not called from outside
  (§6).
- **One concept, one name** — a method, its parameters and its callers use the
  host's term for the thing everywhere; a synonym in one layer is renamed (§1).
- **Minimum surface** — every public method has a caller in this change; one
  the plan lists for a LATER step is written in that step. No "may happen"
  branches (§0).
- **A method taking a row id also takes the tenant key** (`project_id`) and
  treats another tenant's row as absent (§6).
- **Tuning values are module constants, not config**, until a host asks (§6).
- **Enums cross the boundary as enums, never raw ints** (§6); plain
  `enum.Enum`. The Service takes the member as given: converting a request's
  int is the host's job, and the Service neither converts nor re-checks it.
- **A map between two enums is a constant, declared once** — `<SOURCE>_TO_<TARGET>`
  in the constants module of the vocabulary it maps into, imported by every
  service and host that reads it; never a private `_X_TYPES = {...}` dict at the
  top of a service file ("A map between two vocabularies is a constant too" in
  `AGENTS.md`).
- **Unique-constraint races** → `@DuplicateErrorHandler()`, positive
  `if existing: update else: create`, never `try/except IntegrityError` (§6).
  A create whose duplicate is an error does not look the row up first: the
  unique index answers 409 (the `if existing` read is for an upsert only).
- **No read before a write to answer 404/409.** A by-id write is the
  DataAccess `update` under `@Cache(..., invalidate=True)` (the template's
  `update`); let the database and the `RuleValidator` refuse (§6). An
  external API that refuses a duplicate (409 for an existing account) is the
  same: call the create, catch only that status, let every other error out.
  A setting that system already holds (a link lifespan) is set there, never
  sent from code (operator).
- **A delete that records what it removed** (history, an event) reads the row through
  the cached `get` before the delete, under `@Cache(..., invalidate=True)` (§6).
- **Several writes that must land together, or a guard checked before a
  write** (a set-once field, "not answered yet"), run in ONE session the service
  opens through the DA's `transaction()`, with the row read by
  `get_for_update` — each plain CRUD call commits alone, and without the lock
  two concurrent calls both pass the check (§6).
- **A date anchoring a deadline or retention, never correctable later**, is
  refused in the future and before the date it follows (§6).
- **A decorator shipped for hosts** checks its parameter names and derived
  identifiers at decoration time; options after the first are keyword-only (§8).
- **State transitions** (stateful entities) write a history row + an outbox row
  in addition to firing the observer event; pass raw enum/datetime values to
  history `create` (§A4).
- **Invalidate caches on every mutation**, before the observer fan-out (§6).
- **This service is agnostic — it ships the mechanism, never one caller's
  instance of it.** No named instrument/template/preset, no domain vocabulary
  (topic lists, category names, tag sets), no tuned magic number encoding a
  product judgement, and above all **no branch keyed on a specific instance**
  (`if key == FIVE_FACTOR_KEY: return five_factor_definition(...)`). That branch
  is the tell: replace it with a generic codec — store the caller's
  configuration, hand it back, never look at what it means — so a third one is a
  row in a table, not a commit here. A value whose meaning is the host's is
  passed through opaquely; do not read it or branch on it (§4.0). Realistic
  named configurations belong in `tests/` or `examples/`: if the flagship
  example is importable from library source, that is the smell. Litmus:
  **could a stranger build their OWN one without editing a line of this
  library?** See "The library is the TOOL — never an instance of it" in
  `AGENTS.md`.
- **The entity IS the type** — pass entities into pure functions; do not
  declare a parallel `*Definition`/`*DTO` dataclass that mirrors a table. A
  detached instance reads, deep-copies and pickles without a session, which is
  all a mirror class ever bought. A `build_*`/`to_*` function whose body is
  field-for-field assignment is the receipt that a mirror exists. A second type
  is justified only when it carries fields no table has, is a genuinely
  different shape, or is an enforced narrowing — and a rename is none of those.
  Audit what a pure function RETURNS as well as what it takes, and map renames
  before comparing field lists; both hid real mirrors. Expect a transient
  entity to have no column defaults, and expect value equality to disappear.
  See "The entity IS the type" in `AGENTS.md` for the full list.
- **No `@dataclass` in this folder.** `grep -rn "@dataclass" data_layers/service/`
  must return nothing. If a type survives the rule above — it has no table, and
  isn't a mirror of one (what a pure engine returns; an aggregate of several
  entity lists plus computed fields) — it is still DATA, so it goes in
  `data_layers/data/data_types/<snake_case_name>.py`, one class per file.
  **Unless it is error-shaped**: a `ValidationError(code, message)` a validator
  RETURNS, an error code, a failure record — those go to `error_handling/`
  even though they are dataclasses and never raised, because that is the
  library's error vocabulary and it is what the matching exception carries.
  `error_handling/` beats `data_types/` (`core-lib-error-handling`). `service/` holds services and the pure engines they call: behaviour,
  not type declarations. A data type may import entities and other data types
  and **never** a service, DataAccess or engine — that one-way direction is what
  lets any layer import it without a cycle (§4.1).
- **A column name is never a string literal — in any position.** Not just in a
  query or a payload: a `frozenset` of names to strip, a tuple of sort columns,
  a module constant, an `if key == '...'`, a `pop('...')`. All of them read
  `Entity.column.key`. The container matters because of how they FAIL: a stale
  literal in a query usually raises, while a stale literal in a filter set does
  nothing at all — the name stops matching, the column stops being excluded,
  and the suite stays green. That is exactly how a `_NOT_IN_A_TEMPLATE` set
  would have started leaking a tenant's `project_id` into a shared template.
  Only entity declarations (`__table_args__`) and migrations spell names out
  (§4.3). Enforce it with an AST walk over library source, plus a
  "would-this-catch-a-planted-literal" test so an empty result cannot mean the
  walk broke.
- **A payload key that is a column IS the column** — build dicts with
  `{Entity.column.key: value}`, and read them back the same way. Never declare
  a second name for it in `constants/`: not `NORMALIZED = 'normalized'` (a copy
  that drifts on a rename) and not `NORMALIZED = Entity.normalized.key` (an
  alias — a third handle for one string). A `constants/` enum is only for keys
  **no entity owns**: composed names (`delta`, `first_scores`) or one qualified
  to disambiguate a flat payload. A healthy `constants/core_lib_constants.py`
  imports no entity at all. See "The same rule for dict payloads you invent" in
  `AGENTS.md`.

Wire the Service into the main class with `core-lib-main`.
