---
name: core-lib-entity
description: MANDATORY — load this skill BEFORE you add or change any table, model, ORM class, entity, column, field, or nested enum in a *-core-lib; do not write it from memory. Creates one SQLAlchemy entity (Data layer) under data_layers/data/db/entities/ on Base, soft-delete mixins, INTEGER, IntEnum. Pair with core-lib-migration (DDL) and core-lib-data-access (queries).
---

# Create a core-lib entity (Data layer)

The Data layer holds **SQLAlchemy models only** — columns, relationships,
mixins. No queries, no business logic. One file per table under
`<name>_core_lib/data_layers/data/db/entities/`.

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
  (`'workspace_id'`) (§4).
- **Any column with `server_default` MUST also carry the matching Python
  `default=`** (`default=0, server_default='0'`) — otherwise a freshly inserted
  ORM row reads `None` for it before commit (§4).
- **FKs whose children must die with the parent declare it in the schema:**
  `ForeignKey('document.id', ondelete='CASCADE')` (§4).
- Keep this file logic-free; queries belong in a DataAccess (use the
  `core-lib-data-access` skill next), business rules in a Service.

After adding/altering an entity, generate a migration with the
`core-lib-migration` skill.
