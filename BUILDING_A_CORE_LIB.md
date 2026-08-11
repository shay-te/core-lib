# Building a Complete Core-Lib — the architecture guide

This is the **end-to-end guide for architecting a whole `*-core-lib`**: the
mental model, the complete anatomy, the build sequence in order, the decisions
you have to make, and the mistakes to not repeat. Read it before you start a
new library or a substantial feature in one — it exists so you never have to
reverse-engineer "how a core-lib is supposed to be built" from another lib's
diff.

## How the three docs fit together

| Doc | Answers | Use it |
|---|---|---|
| **This guide** (`BUILDING_A_CORE_LIB.md`) | *How do I architect a complete core-lib, in order?* | Read first. The map + the sequence + the mental model. |
| **`AGENTS.md`** | *What are the exact rules for each piece?* | The enforceable conventions (§1–§8). Cited throughout this guide as `§x.y`. |
| **`skills/`** | *Scaffold this one part for me now.* | Copy-paste-ready templates, one per part. The MANDATORY routing gate in `AGENTS.md` says which to load. |

This guide gives **structure and sequence**; `AGENTS.md` gives **rules**;
`skills/` give **templates**. When they overlap, the rule text lives in
`AGENTS.md` and is referenced here, not duplicated.

---

## 1. The mental model — what a core-lib *is*

A core-lib is where your application's **business logic lives**, with every
framework and external service plugged in from the outside. Internalize four
properties; every rule downstream follows from them:

- **Onion architecture.** Three concentric layers — `data → data_access →
  service`. Outer may call inner; **never the reverse**. Entities know nothing
  about queries; queries know nothing about business rules; business rules know
  nothing about HTTP.
- **POPO (Plain Old Python Objects).** No framework lock-in. The library runs
  headless in tests and plugs into Flask/Django/CLI/a worker equally. It never
  imports `request`, a web session, or a live DB at import time.
- **Composable.** A core-lib is a plugin. It can embed another core-lib and be
  embedded by a host app, all through config — never by importing a sibling
  library peer-to-peer (§2.4).
- **Agnostic.** It knows **nothing** about the host that consumes it — no brand,
  no host env-var names, no host-specific text. Everything host-specific is
  *injected* (constructor param / function arg) with a safe neutral default.
  This is non-negotiable; see the "this library is AGNOSTIC" block in
  `AGENTS.md` and section 11 below.

The payoff: swapping Flask for FastAPI, Postgres for SQLite, or one SDK for
another touches the **edge**, never the business logic.

---

## 2. The complete anatomy

```
<name>-core-lib/                          # the git repo (dashes)
├── <name>_core_lib/                      # the package (underscores)
│   ├── config/
│   │   └── <name>_core_lib.yaml          # Hydra config: data, cache, jobs…
│   ├── data_layers/
│   │   ├── data/
│   │   │   ├── db/
│   │   │   │   ├── entities/             # (1) SQLAlchemy models — one file/table
│   │   │   │   └── migrations/versions/  #     Alembic revisions
│   │   │   └── <dataclasses & data enums>#     value objects live under data/
│   │   ├── data_access/                  # (2) pure-CRUD query classes
│   │   └── service/                      # (3) business logic, caching, public API
│   ├── connections/                      # outbound SDK/API clients (optional)
│   ├── jobs/                             # background tasks (optional)
│   ├── error_handling/                   # typed errors (optional)
│   └── <name>_core_lib.py                # the main class — composition root
├── hydra_plugins/<name>_core_lib/        # advertises this lib's config to hosts
├── tests/
├── setup.py / pyproject.toml
└── requirements.txt                      # just `core-lib` (+ extras_require)
```

**The one dependency arrow that matters:** `service → data_access → data`.
Nothing flows the other way. Lock it with a boundary test (§2.4) if the lib has
a lower/transport layer another layer must not import.

---

## 3. The three layers, in depth

### Layer 1 — Data (`data_layers/data/`)
SQLAlchemy entities (one file per table) plus plain value objects (`@dataclass`,
data enums). **No queries, no logic.** Entities carry columns, relationships,
mixins, and their own nested enums.
- Soft-delete via `SoftDeleteMixin` (adds `created_at`/`updated_at`/`deleted_at`);
  add `SoftDeleteTokenMixin` when a unique constraint must survive
  soft-delete + re-insert.
- **Rules:** §3.5 (`INTEGER`), §3.7 (`server_default` pairing), §4.2 (enum type).
- **Skill:** `core-lib-entity`. **Then** `core-lib-migration` for the DDL.

### Layer 2 — DataAccess (`data_layers/data_access/`)
**Pure CRUD over one entity** — insert one, fetch one, update one by PK,
soft-delete one by PK, list by simple filters. That is the whole job.
- Extend the right core-lib base: `CRUDDataAccess` (hard delete),
  `CRUDSoftDeleteDataAccess`, or `CRUDSoftDeleteWithTokenDataAccess`.
- **Rules:** §3.1 (no logic here — reconciliation/scoping is the service's job),
  §3.2 (soft-deleted rows are never returned), §3.3 (entity-introspection
  writes), §3.4 (column names from the entity), §3.6 (one DB statement per
  named method).
- **Skill:** `core-lib-data-access`.

### Layer 3 — Service (`data_layers/service/`)
Business logic, caching, transformation. **This is the library's public API
surface.** Callers reach the lib only through
`core_lib.some_service.some_method(...)` — never into a DataAccess.
- **Rules:** §4.1 (public vs private surface), §4.2 (enum boundaries), §4.3
  (unique-constraint races), §4.4 (when to cache), §4.5 (cache keys,
  invalidation, decorator order), §4.6 (state transitions → history + outbox +
  observer), §4.7 (invalidate on mutation), §4.8 (shared private core), §4.9
  (redaction).
- **Skill:** `core-lib-service`.

---

## 4. The composition root — the main class

`<name>_core_lib.py` wires the layers together. Two hard rules: call
`CoreLib.__init__(self)` **first**, and expose **only services** as public
attributes (never a DataAccess — that leaks cache misses and raw ORM rows past
the boundary).

```python
class MyCoreLib(CoreLib):
    def __init__(self, config: DictConfig):
        CoreLib.__init__(self)                 # FIRST — wires event listeners
        self.config = config
        db = instantiate_config(self.config.core_lib.data.db, SqlAlchemyConnectionFactory)
        if not CoreLib.cache_registry.registered():        # host may pre-register redis
            CoreLib.cache_registry.register('my_core_lib', CacheHandlerRam())
        self.widgets = WidgetService(WidgetDataAccess(db))  # public API surface
```

A `MyCoreLibInstance` singleton (`init(cfg)` / `get()`) is the conventional
accessor. **Skill:** `core-lib-new` scaffolds all of this.

Registries (`CoreLib.cache_registry`, `.connection_factory_registry`,
`.observer_registry`) are in-memory and class-level; the lib registers a default
only when empty so a host can override.

---

## 5. Config & wiring (Hydra)

The lib ships `config/<name>_core_lib.yaml`; a host overrides the sections it
cares about. Connection factories are declared with a `_target_` + `config`
block so Hydra/`instantiate_config` builds them:

```yaml
core_lib:
  data:
    db:
      _target_: core_lib.connection.sql_alchemy_connection_factory.SqlAlchemyConnectionFactory
      config:
        create_db: true
        session: { pool_recycle: 3600, pool_pre_ping: false }
        url: { protocol: sqlite }        # host overrides to its real DB
```

`hydra_plugins/<name>_core_lib/` carries a `SearchPathPlugin` that appends this
lib's `pkg://config` to the search path, so a host app discovers the lib's
config automatically. **Secrets and host-specific values are `${oc.env:...}`
interpolations the host supplies — never hardcoded here** (section 11).

---

## 6. External integrations (when needed)

Talking to an SDK / API / storage / gateway? It goes in `connections/` as a
**factory + connection pair**, never inline in a service — that's what keeps the
SDK swappable at the edge.

- **Rules:** §5.1 (the factory/connection shape), §5.2 (lazy SDK import), §5.3
  (typed errors), §5.4 (optional SDKs in `extras_require`), §5.5 (registries
  stay in-memory).
- **Skill:** `core-lib-connection`.

---

## 7. Testing strategy

Tests live inside the library and test **only** the library. The shape to aim
for: a per-layer test that wires the *real* collaborators (service over real
DataAccess over in-memory SQLite), plus **one `test_flow.py`** driving the
primary workflow A→Z.

- **Rules:** §7.1 (one `TestCase` per file), §7.2 (real collaborators, the mock
  litmus test). Coverage and fixture rules live in the AGNOSTIC block's
  "Self-contained and fully tested".
- **Skill:** `core-lib-tests`.

---

## 8. Packaging & dependencies

A core-lib depends on `core-lib` and little else — `SQLAlchemy`, `alembic`,
`omegaconf`, and `hydra-core` arrive transitively, so re-declaring them is a
smell. Anything a caller might never use is an **opt-in extra**, not a hard
dependency.

**Rules:** §5.4 (`extras_require` + lazy import), §2.1 (empty `__init__.py`, no
re-export facades).

---

## 9. The build sequence — from empty repo to working lib

Follow in order; each step names the skill to load and the rules it enforces.
Skipping a step is how libraries end up half-wired.

1. **Scaffold the tree** (section 2) and the composition root — `core-lib-new`.
2. **Model the first entity** — `core-lib-entity` (§3.5, §3.7, §4.2).
3. **Generate its migration** — `core-lib-migration`.
4. **Add its DataAccess** — `core-lib-data-access` (§3.1–§3.4).
5. **Add its Service** (public API) — `core-lib-service` (§4.x).
6. **Wire the service** as a public attribute on the main class (§4-intro).
7. **Config + hydra plugin** so a host can embed and override (section 5).
8. **External clients** if any — `core-lib-connection` (§5.1–§5.5).
9. **Tests**: per-layer + one `test_flow.py`, 100%, agnostic — `core-lib-tests`.
10. **Verify the Definition of Done** (section 12 checklist below).

Repeat 2–5 (the vertical slice) per new entity/domain.

---

## 10. Decision guide — the choices that get missed

| Question | Answer |
|---|---|
| Which DataAccess base? | Hard delete → `CRUDDataAccess`. Soft delete → `CRUDSoftDeleteDataAccess`. Soft delete + unique-constraint re-insert → `CRUDSoftDeleteWithTokenDataAccess`. |
| Cache this read? | Only if another service asks it repeatedly in one request. Host PK-by-id read → no; record *why not* in the service docstring (§4.4). |
| How is an enum stored? | Plain `enum.Enum` on the entity, `Column(IntEnum(MyEnum))` for storage; it crosses the service boundary as the enum, never a raw int (§4.2). |
| Reconcile / find-or-create? | In the **service** (call DA methods), never in the DataAccess (§3.1). |
| New external SDK? | Connection-factory shape + `extras_require` + lazy import (section 6). |
| A "spec"/ruleset as data? | Frozen dataclass DSL owned by the consumer, not a nested dict (§2.2); generic engine in its own file (§2.3). |
| Host needs custom text/behavior? | Inject it as a param with a neutral default — never reach back into the host (section 11). |

---

## 11. The recurring mistakes — what the AI keeps getting wrong

These are the gap-closers. Each is a real, repeated mistake; the fix is the rule
in parentheses.

1. **Leaking the host into the lib** — hardcoding a product name, a host env-var,
   or host-specific prompt/wording. Inject it instead ("AGNOSTIC" block).
2. **Business logic in the DataAccess** — `if exists update else insert`,
   "restore" branches, tenant scoping. Move it to the service (§3.1).
3. **Exposing a DataAccess** on the main class. Expose services only (§4-intro).
4. **Caching every `get`** — bloats invalidation reasoning. Cache only
   cross-service hot paths (§4.4).
5. **Wrong decorator order** — `@Cache` must sit *outside* `@ResultToDict`;
   `@DuplicateErrorHandler` outermost (§4.3, §4.5).
6. **`try/except IntegrityError`** for unique races instead of
   `@DuplicateErrorHandler`, or re-querying to "recover" the winner (§4.3).
7. **Hardcoded column strings** `'name'` instead of `Entity.name.key`; whitelist
   constants instead of entity introspection (§3.3, §3.4).
8. **`Integer` instead of `INTEGER`**; a `server_default` with no Python
   `default` (§3.5, §3.7).
9. **Raw ints across the service boundary**; using `enum.IntEnum` (§4.2).
10. **`assert` for arg validation** in your own methods (stripped under `-O`) —
    use `raise` (§1.5).
11. **Re-export-only `__init__.py`** facades; importing a sibling lib
    peer-to-peer (§2.1, §2.4).
12. **`requirements.txt` bloat** — adding optional SDKs instead of
    `extras_require` + lazy import (§5.4, section 8).
13. **Over-mocked tests** that pass green while the real path is broken; multiple
    `TestCase`s per file (§7.1, §7.2).
14. **Config with inline defaults / aliases** instead of fetch → validate → use
    (§1.1).

If you catch yourself re-explaining one of these in a prompt, it belongs in
`AGENTS.md` — add it there so it's enforced next time, not re-typed.

---

## 12. Definition of Done — a complete core-lib

- [ ] `service → data_access → data` layering intact; no reverse imports.
- [ ] Every entity has a DataAccess and (if it has a public API) a Service.
- [ ] Services are the only public attributes on the main class.
- [ ] Main class calls `CoreLib.__init__(self)` first; registers a default cache
      only when the registry is empty.
- [ ] Config yaml + hydra plugin present; a host can embed and override; no
      hardcoded secrets/host values.
- [ ] Migrations exist for every entity and run + roll back cleanly.
- [ ] Tests: per-layer real-collaborator tests + one `test_flow.py`, 100%
      coverage, one `TestCase` per file, agnostic fixtures.
- [ ] `requirements.txt` is just `core-lib` (+ `extras_require`); `__init__.py`
      files are empty markers.
- [ ] Fully agnostic — passes the agnosticism litmus test: a stranger could
      publish and use it without learning what app it came from.
