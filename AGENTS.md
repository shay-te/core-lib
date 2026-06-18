# AGENTS Notes — core-lib (canonical rulebook for every `*-core-lib`)

> **This file is the single, generic rulebook for every `*-core-lib` package
> in the workspace — present or future.** It consolidates the rules that were
> previously scattered across the individual `*-core-lib/AGENTS.md` files so
> that anyone writing a new core-lib library starts out knowing all of them.
>
> Every rule below is stated **generically** — substitute your own entity,
> service, config, and connection names for the placeholders (`Entity`,
> `MyService`, `MyConnectionFactory`, `my_field`, …). Nothing here is tied to
> a specific core-lib; repo-specific lessons stay in that repo's own
> `AGENTS.md`.
>
> For the framework's folder layout, the three data layers, decorators, the
> main-class composition root, Hydra config, and migrations, also read the
> **"core-lib framework conventions"** section in `architecture.md`. Where a
> rule below has a canonical home elsewhere, it is cross-referenced; the rule
> itself is restated here so this file is self-contained.

---

## 1. Coding conventions (apply to every Python file)

### 1.1 Fetch → validate → use, always in that order

> Canonical home: `architecture.md` → "Coding conventions (workspace-wide,
> all Python repos)". Restated here because it is the most-applied rule in
> the workspace.

Any method that pulls fields out of an external value source — a Hydra
`DictConfig` / plain `dict`, a raw SDK response object, a config dataclass,
an HTTP response payload, anything you reach into with `.get(...)` or
`getattr(...)` — must be structured as **three explicit, contiguous blocks**,
in this order:

1. **fetch** — pull every field the method touches into a named local at the
   top, one line per field (`region = config.get('region')`,
   `block_text = getattr(block, 'text', None)`). One read per value.
2. **validate / normalize** — every None / falsy check, every
   `raise SomeError(...)`, every "fall back to the request model when the SDK
   omitted one", in one contiguous block immediately after the fetch.
3. **use** — assign to `self.*`, build the SDK payload, construct the public
   dataclass, return — all from already-named, already-validated locals.

Add `# 1. fetch` / `# 2. validate` / `# 3. use` markers when the blocks
aren't already obvious; they double as anchors for the next reviewer.

Hard rules inside this pattern:

- **No fallback defaults inline.** `config.get('region', 'us-east-1')` is
  banned — it hides the requirement. Pull the value bare and raise in step 2
  if it's missing. The only acceptable inline default is on a value that is
  genuinely optional for the method's behaviour (rare).
- **No aliases inline.** Pick one canonical key per value (`model`, not
  `model_id or model`; `vision_model`, not `vision_model_id`). If a key was
  renamed, callers update — the factory does not paper over it with `or`
  chains.
- **No scattered `.get(...)` / `getattr(...)` inside loops, generator
  expressions, or final return statements.** Inside a `for ... in items:`
  body, fetch the per-iteration fields into named locals at the top of the
  loop body before the conditional / append.
- **Strings use a truthy-check, numerics use `is None`.** `if not model:`
  rejects both `None` and `''`; `if max_tokens is None:` keeps
  `max_tokens=0` valid (a real "let the model decide" signal).

The matching config dataclass mirrors the requirement: every required
cross-cutting field is a required positional field with **no default**, so a
missing value fails loudly instead of silently defaulting.

### 1.2 Variable names — spell out what the value is

Don't abbreviate variable names down to one or two cryptic letters, even in
tests. A reader should be able to tell from the name alone what the value
holds. This applies to parameters, locals, comprehension variables, and
tuple destructuring.

- **Banned abbreviations** (illustrative, not exhaustive): `cfg`, `ws`,
  `ws_id`, `s` (for "service"), `c` (for "collection"), `d` (for
  "document"), `r` (for a row/entity), `bf` (for a factory). Rename to the
  full entity / role: `config`, `workspace`, `workspace_id`, `service` (or
  the specific service name), `collection`, `document`, `bedrock_factory`.
- **`row` is banned when the variable holds a domain entity** — use the
  entity name (`workspace`, `collection`, `document`). Keep `row` only when
  the value is genuinely a DB row that doesn't map to one of our entities.
- **Helper names too**: a helper called `mk(...)` becomes
  `_make_collection(...)`; `_service()` becomes `_workspace_service()`.
- **OK**: `i` / `j` / `n` as numeric counters; `e` / `exc` in `except`
  blocks; pythonic `self` / `cls`; `id` / `db` (already full words).

### 1.3 No single-letter loop variables (except `i` / `j`)

> Canonical home: `architecture.md` → workspace-wide conventions.

Loop variables and comprehension bindings get **meaningful names** in both
production code and tests. `for row in rows`, `for document in documents`,
`for cell in row`, `for candidate in candidates` — never `for r in rows`,
`for d in docs`, `for k in storage.blobs`. The only allowed single letters
are `i` / `j` as canonical integer counters in `range(...)` loops; everything
else (`a`, `b`, `c`, `d`, `e`, `k`, `n`, `o`, `p`, `r`, `s`, `t`, `v`, `x`,
…) is banned. Tuple unpacking follows the same rule:
`left, right = sets[i], sets[j]`, not `a, b = sets[i], sets[j]`.

### 1.4 Parameter / argument lists — one line, or one per line (never packed)

A signature or call is **all-on-one-line OR one-per-line — never packed
multiple-per-line.** If it fits on one line, keep it on one line; if it must
wrap, put every parameter (and `self`) on its own line.

```python
# One line:
def send(self, email, org_id): ...

# One per line:
def send(
        self,
        email: str,
        org_id: int,
        due_date,
):
    ...

# NOT: several params grouped on a wrapped line
# def send(self, email: str, org_id: int,
#          admin_name, recipient_name): ...
```

### 1.5 Validate with `raise`, not `assert` (production code)

`assert` is stripped when Python runs under `-O`, so it must never carry
argument / precondition validation in DataAccess or Service code. Use
`if not ...: raise ValueError(...)` (or the appropriate exception) so the
check survives optimized runs. `assert` remains fine in tests and in
import-time invariants meant to fail fast in dev. Each required-arg guard
should have a covering negative test.

### 1.6 Keep functions simple — static analysis can block the PR

These libraries are checked by static analysis (e.g. SonarCloud); small
readability warnings can block a PR. Keep functions below the cognitive-
complexity threshold and avoid nested conditional expressions:

- When a function trips a cognitive-complexity warning, extract small private
  helpers (e.g. an `_empty_result(...)` / `_coalesce_value(...)` helper) that
  preserve behaviour while reducing branching.
- Replace nested ternary / conditional expressions with an independent
  statement or a small helper rather than inlining a second `... if ... else`
  inside another.
- Treat the module that *defines* a public name as the single source of truth
  for that name. Before mass-renaming an exported helper, scan the repo with
  `rg` for both imports and call sites.

---

## 2. File & package organization

### 2.1 No empty / re-export-only files

Do not create files whose only content is boilerplate or pure re-exports. In
particular, do not write `__init__.py` aggregators that list
`from .x import Y` for every submodule — they pull no weight and are noise in
the diff.

- When Python requires an `__init__.py` for package discovery, leave it
  **empty** (a package marker). Empty-marker beats noisy-aggregator. The
  package-root `__init__.py` may hold only `__version__`.
- Import from the **defining submodule** at the consumer site —
  `from my_core_lib.connections.bedrock_connection_factory import BedrockConnectionFactory`,
  not `from my_core_lib.connections import BedrockConnectionFactory`, and not
  from a package-root facade.
- Don't split a subpackage into multiple files just to "feel organized" —
  split only when modules carry meaningfully different responsibilities.
- Don't create a file just so it can be listed in a validation report. Every
  file in a PR should do real work.

---

## 3. Data layer (DataAccess)

### 3.1 DataAccess is pure CRUD — logic lives in services

DataAccess classes are **pure CRUD**: insert one row, fetch one row, update
one row by PK, soft-delete one row by PK, list rows by simple filter kwargs.
That's it. What does **not** belong in a DataAccess method:

- `if exists update; else insert` reconciliation.
- "Restore a soft-deleted row" branches.
- Cross-row look-ups that decide what to write next.
- Workspace / project / tenant scoping (that lives in the service).

If a flow needs any of the above, the **service** orchestrates it by calling
multiple DA methods (e.g. the service calls `get_by_...()` then either
`update(...)` or `create(...)` — the DA never contains the "is there already
a row?" decision). This keeps DA methods trivially testable and the service
layer the single place to read business rules from.

### 3.2 DataAccess never returns soft-deleted rows

> Canonical home: `architecture.md` → "The three data layers".

Every read method (`get`, `get_by_*`, `all`, …) filters
`deleted_at == None` unconditionally. Do **not** add an `include_deleted`
parameter (or any other knob) that lets a caller ask for soft-deleted rows
back — soft-deleted means tombstoned and invisible to the application.

If a service-layer flow needs to "restore" a previously soft-deleted row,
that's a schema problem, not a DataAccess problem: use `SoftDeleteTokenMixin`
so the unique constraint scopes to active rows and a fresh `INSERT` succeeds
without the DA ever peeking at deleted state.

### 3.3 Writes use entity introspection, not whitelist constants

When a DataAccess `create` / `update` accepts a `data: dict`, the entity is
the single source of truth for what's writable. Don't define module-level
`_CREATABLE_FIELDS` / `_MUTABLE_FIELDS` sets — they duplicate the entity
schema and rot the moment a column is added. Canonical loop:

```python
entity = Entity()
for key, value in data.items():
    if key == 'id' or not hasattr(entity, key):
        continue
    if isinstance(value, Enum):
        value = value.value
    setattr(entity, key, value)
```

Three load-bearing pieces:

- **`hasattr(entity, key)`** filters typos and externally-supplied keys —
  only real columns get written.
- **`key == 'id'`** is explicit — the PK is never reassignable from a
  payload, even if the caller asks for it.
- **`isinstance(value, Enum)`** unwraps enum members to their stored `.value`
  so callers can pass an enum member without knowing which columns store
  strings vs. members.

For `update`-style flows, fetch the row and run the same loop against the
loaded instance, returning rowcount based on whether anything changed. A DA
that gates writes with a strict-mode rule validator gets the same outcome —
the rule is "no whitelist constants either way".

### 3.4 Entity column names come from the entity — never hardcode the string

> Canonical home: `architecture.md` → "The three data layers".

Anywhere code refers to a column by name — create/update payload dicts, field
allowlists, `data.get(...)` / `data.pop(...)` / `key in data` look-ups, rule
validators — take the name from the entity via `.key`:

```python
{Entity.my_field.key: value}   # correct
{'my_field': value}            # wrong
```

Column renames then propagate atomically from the single source of truth.

**Migrations are the only exception** — a migration pins the physical DDL at
the moment the revision was written and must not drift when the entity later
changes. (Corollaries: `ForeignKey` / `Index` / `UniqueConstraint` strings
declared *inside* the entity class sit next to the columns they name and are
part of the entity definition; entity-schema tests that assert physical
column names keep literals on purpose, else the assertion is a tautology.)

### 3.5 Use `INTEGER`, not `Integer`

In every entity definition and every Alembic migration, integer columns use
the explicit SQL-standard form:

- Entities: `from sqlalchemy import INTEGER` and `Column(INTEGER, ...)`.
- Migrations: `sa.Column('id', sa.INTEGER(), ...)`.

Not the generic `sqlalchemy.Integer` alias.

---

## 4. Service layer

> The service layer owns business logic, caching, and transformation, and is
> the library's public API surface. Callers outside the core-lib go through
> `core_lib.some_service.some_method(...)` — never into a DataAccess directly.

### 4.1 Public surface vs private internals

A service's public methods are its contract. Private internals (the
`_mark_*` / `_create` / `_update_*` / `_overwrite_active`-style helpers,
prefixed with `_`) are **not** to be called from outside the service. Expose
a single bulk / public entry point for each external concern and keep the
step methods private.

### 4.2 Enums cross the service boundary as enums — never raw ints

> Canonical home: `architecture.md` → "The three data layers" (Enum
> boundaries).

When a service method parameter semantically *is* one of an entity's nested
enums, the signature declares the enum type and the body enforces it with an
explicit raise — never declared `int` and coerced internally via
`Enum(value)`:

```python
def grant(self, ..., permission: Entity.Permission, ...):
    if not isinstance(permission, Entity.Permission):
        raise ValueError('permission must be an Entity.Permission member')
```

Callers pass `Entity.Permission.READ`, not `.READ.value`; a raw int (valid or
not) fails loudly instead of being silently coerced. Scalar reads hand the
member back too.

**Use plain `enum.Enum`, not `enum.IntEnum`** — `IntEnum` subclasses `int`,
so a member would be silently usable wherever an `int` is accepted (the exact
failure mode this rule prevents). DB storage still works through the core-lib
`IntEnum` SQLAlchemy decorator (`Column(IntEnum(Permission), ...)`), which
calls `.value` on write and `Permission(value)` on read — neither path needs
the Python type to extend `int`.

The DA's rule validator types the field as the **enum class** too, not `int`,
so a future caller that bypasses the service can't sneak a raw int through the
DA boundary. Raw `.value` ints exist only inside serialized payloads
(`@Cache`/`@ResultToDict` dicts and DB rows) — don't "fix" those.

### 4.3 Unique-constraint races — `DuplicateErrorHandler`, no `try/except`

When a service writes a row whose entity carries a `UniqueConstraint`, **do
not** wrap the call in `try: ... except IntegrityError:`. Decorate the method
with `core_lib.error_handling.duplicate_error_decorator.DuplicateErrorHandler`
instead — it catches the DB violation and raises an HTTP 409 CONFLICT; the
HTTP caller retries or surfaces 409 to the user, and the service stays linear.

Corollary: **do not re-query after `IntegrityError` to "recover" the winner's
row.** The pre-check above the create already covers the "row exists →
update" case, so an `IntegrityError` necessarily means a concurrent insert
won the race — the right answer is 409, not a recovery path that overwrites a
row another caller just wrote. Write the fork as a **positive**
`if existing: update; else: create`.

Decorator order: `@DuplicateErrorHandler()` sits **outside** `@ResultToDict()`
(the exception path doesn't touch the return value; keeping the error
decorator outermost matches the cache-decorator convention).

### 4.4 Cache where the win is real — not on host-read PK lookups

> Canonical home: `architecture.md` → "The three data layers" (caching).

A `@Cache` belongs only where service A repeatedly asks service B the same
question inside a single request (e.g. a workspace-id resolution hit by every
other service, an existence check hit by every permission check). Host-app
PK-by-id reads (one read, then render) **don't** get caches: the indexed
lookup is microseconds, and the bookkeeping (key shape, invalidation, hidden
invariants, future cascade-evict walkers) is real mental tax that compounds
for every reviewer.

When you decide **not** to cache a service `get`, write that reasoning into
the service-class docstring so the next reviewer doesn't add `@Cache` back.

### 4.5 Cache-key / invalidation invariants

For the caches you *do* keep:

1. **Decorator order**: `@Cache(KEY)` **outside** `@ResultToDict()`. Cache
   handlers only accept JSON-serializable values, so the row must already be a
   dict when it reaches the cache. Consequence: a cached getter returns a
   **dict** — service-internal consumers read fields as `row[Entity.col.key]`,
   not `.attr`.
2. **The key template names every parameter the value depends on** (e.g.
   `'my_document_{project_id}_{document_id}'`), unless that dependency is
   re-checked outside the cache on every call. Key templates are module-level
   constants above the class.
3. Gates against an **immutable relationship** (a row's scope id never
   changes) may run inside the cached body — they execute at fill time only. A
   gate against **another entity's mutable row** must run *outside* the cache
   on every call, against that entity's *cached service getter*, so a cached
   child never outlives its parent.
4. **Every method that writes a row directly through the DA** carries
   `@Cache(SAME_KEY, invalidate=True)`. Orchestrators that write only via
   other service methods need no decorator — the methods they call already
   evict.
5. When the writer can't template the key it must evict (different params),
   add a private **empty-body eviction hook** decorated
   `@Cache(KEY, invalidate=True)` and call it.
6. **`create` never evicts** — the decorator never caches `None`/misses, so
   there's no stale negative entry. But a **write-then-return-the-row** flow
   must **evict first, then re-read through the cached getter**, or it returns
   the pre-write cached row.
7. **`list` / `search` / `all` stay uncached** — `limit` / `offset` / `query`
   make the key space unbounded, so a writer could never enumerate the keys to
   evict.
8. The lib's main class registers a default `CacheHandlerRam` **only when the
   registry is empty** (`if not CoreLib.cache_registry.registered()`), so a
   host can pre-register redis/memcached before constructing the lib. Tests
   reset the registry per test so cached rows never leak between tests reusing
   the same ids.

### 4.6 State transitions — history + outbox + observer event

Where a service models a stateful entity, every state transition should, in
addition to firing the observer event, write:

- a **history row** (a full snapshot of the changed fields), and
- an **outbox row** (an event log, with optional async-worker metadata),

so downstream consumers and audit trails stay consistent. Pass **raw values**
(enum members, native `datetime` objects) to the history service's `create`
— not values already converted by `@ResultToDict` — because the DA's
`setattr` loop converts `Enum` → `.value` itself.

### 4.7 Invalidate caches on every mutation

Mutations call the service's cache-invalidation helper right before the
observer fan-out. When you add a new cached read that could ship stale data
after a write, add it to that helper.

---

## 5. Connections & external clients

### 5.1 The connection-factory shape

Outbound integrations (LLM providers, object storage, payment gateways, any
external SDK) follow one shape, the same for every backend present or future:

- `MyConnectionFactory(core_lib.connection.ConnectionFactory)` — takes a
  `Mapping` / `DictConfig`, builds the shared SDK client **once** in
  `__init__` (via fetch → validate → use), and exposes `get()` returning a
  fresh `MyConnection`.
- `MyConnection` — the per-call surface (e.g. `complete_text(...)`,
  `embed(...)`, `list(...)`, `close()`), returning / accepting a shared
  envelope dataclass.

Do **not** reintroduce a parallel generic provider ABC with a different
method surface alongside the factory style — standardize on one. New
capabilities (streaming, multi-turn, tool calls) belong in separate per-call
helpers, not a second parallel API.

### 5.2 Lazy SDK imports inside `_build_client`

Each factory's `_build_client` does the heavy SDK import **inside the method
body**, not at module top. This keeps an install that only uses one backend
from importing the other backends' trees on package import. Tests inject a
fake client through config (e.g. `config['client']`) so the SDK build path
stays untouched by the suite.

### 5.3 Errors are typed, not stringly-checked

Catch the specific error class — never parse error messages. Every connection
wraps the underlying SDK's exceptions in the library's own typed error
(`MyProviderError`-style) so callers never need to import the SDK's exception
hierarchy. Define a small typed-error set (config error, missing/duplicate
connection, invalid provider, provider error) and raise those.

### 5.4 Dependencies — depend on `core-lib`; optional backends in `extras_require`

Keep `requirements.txt` minimal: depend on `core-lib`, and let the common
transitive deps (`SQLAlchemy`, `alembic`, `omegaconf`, `hydra-core`, etc.)
arrive through it rather than re-declaring them. Optional/heavy backend SDKs
(e.g. `openai`, `anthropic`, `boto3`) go in `extras_require` so consumers opt
in (`pip install 'my-core-lib[openai]'`) — do not add them to
`requirements.txt`.

### 5.5 In-memory registries — no persistence

A connection/handler registry is in-memory by design. Re-register on process
boot. Don't add a DB-backed implementation inside the library — that belongs
in a host app or a separate library that *consumes* this one.

---

## 6. Enums

### 6.1 Priority-ordered enums declare and number members in priority order

When an enum encodes a priority / severity ordering, declare **and** number
its members in that order (e.g. worst-to-best, or lowest-to-highest), so that
iterating the enum yields the priority order directly and downstream code can
rely on `for member in MyEnum:` instead of re-sorting. Document the ordering
intent next to the declaration.

---

## 7. core-lib repo-specific context (applies to this repo only)

> The notes below are specific to the `core-lib` framework repo itself and are
> **not** generic core-lib rules. They are kept here as this repo's own
> `AGENTS.md` context.

- `core_lib/helpers/shell_utils.py` exposes `prompt_*` helpers (not `input_*`
  and not `prompt__*`). The active public prompt helpers are: `prompt_string`,
  `prompt_str`, `prompt_file_name`, `prompt_yes_no`, `prompt_bool`,
  `prompt_int`, `prompt_email`, `prompt_url`, `prompt_timeframe`,
  `prompt_enum`, `prompt_options`, `prompt_list`, `prompt_comma_list`.
- Treat `core_lib/helpers/shell_utils.py` as the source of truth for exported
  prompt-helper names. Before mass-renaming prompt helpers, scan the repo with
  `rg` for both imports and call sites.
- Keep prompt helpers simple — this repo is checked by SonarCloud and small
  readability warnings (cognitive complexity, nested conditional expressions)
  can block PRs. The private helpers `_empty_prompt_result` and
  `_coalesce_prompt_value` in `shell_utils.py` exist to keep behaviour the
  same while reducing branching; reuse that pattern rather than re-introducing
  nested conditionals.
