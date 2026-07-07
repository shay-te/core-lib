---
name: core-lib-entity
description: Scaffold a SQLAlchemy entity (the Data layer) for a *-core-lib — a table class under data_layers/data/db/entities/ with the right Base, soft-delete mixins, IntEnum columns, and INTEGER columns. Use when asked to add a new table, model, or entity to a core-lib, or when starting a new data domain that needs persistence.
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

from sqlalchemy import Column, INTEGER, VARCHAR, Date

from core_lib.data_layers.data.db.sqlalchemy.base import Base
from core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_mixin import SoftDeleteMixin
from core_lib.data_layers.data.db.sqlalchemy.types.int_enum import IntEnum


class Widget(SoftDeleteMixin, Base):
    __tablename__ = 'widget'

    class Status(enum.Enum):          # plain Enum, NOT IntEnum
        DRAFT = enum.auto()
        ACTIVE = enum.auto()

    id = Column(INTEGER, primary_key=True, nullable=False)
    name = Column(VARCHAR(length=255), nullable=False)
    status = Column(IntEnum(Status), nullable=False)
    created_on = Column(Date)
```

## Mixins (pick one delete strategy)

- `SoftDeleteMixin` → adds `created_at`, `updated_at`, `deleted_at`.
- `SoftDeleteTokenMixin` → adds `deleted_at_token` (int; `0` = active, non-zero
  = ms timestamp). Add this **in addition** when a unique constraint must let a
  fresh insert succeed after a soft-delete (indexing a DateTime is slow; the
  token scopes uniqueness to active rows).
- Neither → hard-delete table.

## Rules to enforce (from AGENTS.md)

- **`INTEGER`, not `Integer`** — explicit SQL-standard form everywhere
  (§3.5).
- **Nested enums are plain `enum.Enum`, never `enum.IntEnum`** (§4.2). DB
  storage goes through the `IntEnum(...)` column type, which converts
  `.value` on write and `Enum(value)` on read — the Python type must not
  extend `int`.
- **Priority-ordered enums** declare and number members in priority order so
  iteration yields that order (§6.1).
- Keep this file logic-free; queries belong in a DataAccess (use the
  `core-lib-data-access` skill next), business rules in a Service.

After adding/altering an entity, generate a migration with the
`core-lib-migration` skill.
