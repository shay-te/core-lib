---
name: core-lib-entity
description: MANDATORY — load this skill BEFORE you add or change any table, model, ORM class, entity, column, field, or nested enum in a *-core-lib; do not write it from memory. Creates one SQLAlchemy entity (Data layer) under data_layers/data/db/entities/ on Base, soft-delete mixins, INTEGER, IntEnum. Pair with core-lib-migration (DDL) and core-lib-data-access (queries).
---

# Create a core-lib entity (Data layer)

The Data layer holds **SQLAlchemy models only** — columns, relationships,
mixins. No queries, no business logic. One file per table under
`<name>_core_lib/data_layers/data/db/entities/`.

## ⛔ An entity is DATA. core-lib is NOT Active Record. Read this first.

**`grep -c "def " <your entity file>` must print `0`.** No query methods, no
predicates, no `@property` that derives an answer, no lookup over the entity's
own children. If you are about to write one, stop — it belongs in the service
layer.

```python
# WRONG — Active Record. The entity is answering questions about itself.
class Assessment(Base, SoftDeleteMixin):
    scoring_mode = Column(IntEnum(ScoringMode), nullable=False)

    @property
    def is_categorical(self):
        return self.scoring_mode == ScoringMode.CATEGORICAL

    def scale(self, scale_key):
        return next((s for s in self.scales if s.key == scale_key), None)


# RIGHT — the entity holds the column; the service reads it.
# data_layers/data/db/entities/assessment.py
class Assessment(Base, SoftDeleteMixin):
    scoring_mode = Column(IntEnum(ScoringMode), nullable=False)

# data_layers/service/…  (plain functions, entity as the first argument)
def is_categorical(assessment) -> bool:
    return assessment.scoring_mode == ScoringMode.CATEGORICAL

def scale(assessment, scale_key):
    return next((s for s in assessment.scales or [] if s.key == scale_key), None)
```

**Why, so you can hold the line under pressure.** Every Service returns plain
dicts through `@ResultToDict` — that is the contract with a host. A host
therefore NEVER holds one of these objects. A method on an entity is reachable
only from inside the library, by code already in the service layer that could
have called a function. It buys nothing, and it costs the layering: `data/`
starts holding logic, and `service/` stops being the only place that knows how
a thing is interpreted.

It also drags the entity somewhere it must not go. `is_categorical` needs the
`ScoringMode` enum; a lookup over children needs to know children exist. Soon
`data/` — the layer everything else depends on — depends back.

**No exception — not even an `__init__`.** If an entity must accept a
NON-COLUMN kwarg (a child collection attached when a row is read as part of a
larger object), declare it as a plain class attribute with a safe empty
default:

```python
class Thing(Base):
    id = Column(INTEGER, primary_key=True)
    children = ()          # not a column — a default, and a declaration
```

SQLAlchemy's declarative constructor accepts any kwarg for which
`hasattr(type(self), key)` holds, so `Thing(children=[...])` already works.
Writing a mixin that pops those kwargs and re-sets them reimplements the base
class — check what SQLAlchemy already does before adding one.

**Where the logic goes:** the service layer, as plain functions taking the
entity first. If several services need them, one module owns them; import the
MODULE and qualify the call (`definition_loader.scale(...)`), because the bare
names collide with the local variables these functions get assigned to.

See "An entity is DATA. core-lib is not Active Record." in `AGENTS.md`.

## ⛔ This is where agnosticism is usually lost. A schema is the hardest thing to walk back.

A core-lib is **product-agnostic**: it ships the mechanism, and every particular
configuration of that mechanism belongs to the caller. An entity is where that
gets broken, because a column is where a vocabulary gets written down. Neither
form below contains a product name, so the brand-name check misses both.

**1. A column whose MEANING is the host's is an opaque scalar. Store it; never read it.**

```python
cadence = Column(IntEnum(Cadence))    # ⛔ WEEKLY/MONTHLY/QUARTERLY — one product's schedule
cadence = Column(INTEGER)             # ✅ opaque; the host defines the value AND owns the scheduling
```

The enum forces every host onto the three intervals whoever wrote it happened
to need, and once the library owns the members something eventually branches on
them. Take the value, persist it, hand it back — and say so in the docstring,
because the next author's instinct is to "improve" the INTEGER into an enum:

> `cadence` is OPAQUE to this library. The host defines the meaning of the
> value and owns all scheduling; nothing here reads it or branches on it. Do
> not add logic keyed on its value, and do not reintroduce an enum.

The check: `grep -rn "<column>"` outside the entity and the migration returns
only the create/read payload — never a comparison.

An enum is right when the LIBRARY branches on the member
(`ScoringMode.WEIGHTED_AVG` selects an algorithm implemented here). It is wrong
when the library only stores and returns it.

**2. An enum the library does branch on must not carry one product's vocabulary.**
Name members for the mechanism, not the instance that prompted them:
`Measures.STATE`/`TRAIT` is a property of assessments in general; a member named
after one questionnaire's category is that questionnaire leaking into the
schema. Of every member ask: *would a completely different customer's instrument
use this word?* If it names **their** thing rather than **a kind of** thing, it
belongs in host data — a row they store — not in a class here.

Same rule for the table: named instruments, presets, topic lists, tag sets,
starter content and tuned magic numbers live in the host, in `tests/`, or in
`examples/` — never in library source. Providing a *shape* is fine; providing
*the* answer set, *the* bands or *the* cutoff is not.

See "The library is the TOOL — never an instance of it" and the two-question
litmus test in `AGENTS.md` (§4.0 for the entity-specific form). The second
question is the one that catches these: **could a stranger build their OWN
instrument on this without editing a line of library source?**

## Steps

1. Pick the table name and columns. Decide soft-delete strategy (see mixins).
2. Create `data_layers/data/db/entities/<entity>.py` with one entity class.
3. Use `INTEGER` (not `Integer`), `VARCHAR(length=...)`, and `IntEnum(...)` for
   enum columns. Declare nested enums as plain `enum.Enum`.
4. If the entity has a `UniqueConstraint` that must survive soft-delete +
   re-insert, add `SoftDeleteTokenMixin` and scope the constraint to active
   rows.

## Canonical template

```python
import enum

from sqlalchemy import Column, VARCHAR, INTEGER, ForeignKey, JSON, Index, UniqueConstraint

from core_lib.data_layers.data.db.sqlalchemy.base import Base
from core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_mixin import SoftDeleteMixin
from core_lib.data_layers.data.db.sqlalchemy.types.int_enum import IntEnum


class ThingKind(enum.Enum):      # SAME file, directly ABOVE the entity — not nested
    ALPHA = 1                    # IntEnum-column values MUST start at 1, never 0 (§12)
    BETA = 2


class Thing(Base, SoftDeleteMixin):        # Base FIRST, then mixins

    __tablename__ = 'thing'                # singular

    INDEX_WORKSPACE_ID = 'ix_thing_workspace_id'      # every index/constraint name
    INDEX_WORKSPACE_NAME = 'ix_thing_workspace_name'  # is a class constant

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    workspace_id = Column(INTEGER, ForeignKey('workspace.id'), nullable=False)
    name = Column(VARCHAR(length=255), nullable=False)
    kind = Column(IntEnum(ThingKind), nullable=False)
    position = Column(INTEGER, nullable=False, default=0, server_default='0')

    __table_args__ = (
        Index(INDEX_WORKSPACE_ID, 'workspace_id', unique=False),
        Index(INDEX_WORKSPACE_NAME, 'workspace_id', 'name', unique=False),
    )
```

## Mixins (pick one delete strategy)

- `SoftDeleteMixin` → `created_at` / `updated_at` / `deleted_at`.
- `+ SoftDeleteTokenMixin` → adds `deleted_at_token` (`0` = live). **Use it
  whenever the table carries a UNIQUE constraint over business columns** — the
  constraint is then declared over `(business_cols…, deleted_at_token)` so a
  soft-deleted row stops colliding with a fresh insert.
- Neither → hard-delete table.

The mixin choice decides the DataAccess base (§5).

## Rules to enforce (from AGENTS.md)

- **This entity IS the type. Nothing else declares its shape.** Do not add a
  parallel `*Definition`/`*DTO`/`*Result` dataclass mirroring these columns, in
  either direction — what a pure function RETURNS is as easy to mirror as what
  it takes, and a rename (`value` for `raw_value`, `id` under another name)
  does not make it a different shape. Pass this class; a detached instance
  reads, deep-copies and pickles with no session. If you find yourself writing
  a `build_*`/`to_*` function whose body is field-for-field assignment, the
  mirror already exists — delete it instead. See "The entity IS the type" in
  `AGENTS.md`, including the six things that bite when you remove one.
- **If it survives that rule, it is a data type — not a service module.** Some
  data genuinely has no table: what a pure engine returns, an aggregate of
  several entity lists plus computed fields, one validation error. Put it in
  `data_layers/data/data_types/<snake_case_name>.py` (one class per file, named
  after the class), never under `data_layers/service/` — that folder is
  behaviour. It may import entities and other data types; never a service,
  DataAccess or engine (§4.1).
- **A column `default=` fires at INSERT, not at construction — leave it that
  way.** An instance built in memory carries `None` where the column says `1`.
  Do NOT add a mixin that applies defaults at construction: every row the
  library reads has already been through INSERT, `validate()` almost certainly
  rejects the missing value already, and supplying it silently SILENCES that
  guard. If a test fixture trips on it, the fixture is missing a value a real
  author would set.
- **`INTEGER`, not `Integer`**; VARCHAR lengths always explicit
  (`VARCHAR(length=255)`; names 512, keys/paths 1024). Free text is `Text`;
  dict payloads are `JSON` columns named `meta_data` (§4).
- **The enum class is plain `enum.Enum`, in the same file directly ABOVE the
  entity — not nested inside it.** Values for an `IntEnum(...)` column **must
  start at 1, never 0** (§4, §12). Storage goes through the `IntEnum(...)`
  column type; the Python type must not extend `int`.
- **Derive enum-based strings from `.name`, not `.value`** — e.g.
  `f'.{kind.name.lower()}'` (§4).
- **Every index / unique constraint gets a class-constant name** referenced
  from `__table_args__` **and** from the migration, so the name lives in one
  place. Inside the class body the *column* references stay string literals
  (`'workspace_id'`) (§4) — this file and the migrations are the **only** two
  places a column name is ever spelled out, because they DECLARE it. Everywhere
  else in the library reads it back as `Entity.column.key`, in every position:
  a query, a payload, a `frozenset` of names, a tuple, a module constant, a
  comparison. A stale literal in a filter set fails silently — the name stops
  matching and the column stops being excluded (§4.3).
- **Any column with `server_default` MUST also carry the matching Python
  `default=`** (`default=0, server_default='0'`) — otherwise a freshly inserted
  ORM row reads `None` for it before commit (§4).
- **FKs whose children must die with the parent declare it in the schema:**
  `ForeignKey('document.id', ondelete='CASCADE')` (§4).
- Keep this file logic-free; queries belong in a DataAccess (use the
  `core-lib-data-access` skill next), business rules in a Service.

After adding/altering an entity, generate a migration with the
`core-lib-migration` skill.
