---
name: core-lib-migration
description: MANDATORY — load this skill BEFORE you add a migration or alter/create/drop any table, column, index, or constraint in a *-core-lib, and right after changing an entity; do not write it from memory. Creates an Alembic revision under data_layers/data/db/migrations/versions/ with matching upgrade/downgrade and sa.INTEGER. The model class itself is core-lib-entity.
---

# Create a core-lib migration (Alembic)

Migrations live in `<name>_core_lib/data_layers/data/db/migrations/versions/`.

## How Alembic is wired — there is NO `alembic.ini`, anywhere

`Alembic(core_lib_path, cfg)` (`from core_lib.alembic.alembic import Alembic`)
builds the Alembic `Config()` **in memory** from the yaml node
`core_lib.alembic`. The lib exposes it via `install()` / `uninstall()`
staticmethods on the CoreLib. Do **not** create an `alembic.ini` and do not
invoke the `alembic` CLI with `-c` (§11.1).

## While the lib is UNRELEASED there is exactly ONE migration

Every schema change during initial development is **folded back into**
`<date>_1_create_db.py` — you do not stack revisions. Only after release do new
revisions get added (§11.2).

## Naming

- File: `<YYYY-MM-DD>_<N>_<reason_slug>.py` — e.g. `2026-06-21_1_create_db.py`.
- `revision` is a bare integer **as a string** (`'1'`, `'2'`, …); `down_revision`
  is the previous number, or `None` for the first. **Never uuid-style ids.**
- Keep `.migration_ver` (in the migrations dir) in sync — it holds the latest
  revision number as plain text. `Alembic.create_migration(name)` maintains it;
  if you hand-write a migration, update it yourself.

## Canonical shape — everything referenced THROUGH the entities

```python
"""create_db

Revision ID: 1
Revises:
Create Date: 2026-06-21 08:26:06.852789

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import ForeignKey

from foo_core_lib.data_layers.data.db.entities.thing import Thing

revision = '1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        Thing.__tablename__,
        sa.Column(Thing.id.key, sa.Integer, primary_key=True, nullable=False),
        sa.Column(Thing.workspace_id.key, sa.Integer, ForeignKey('workspace.id'), nullable=False),
        sa.Column(Thing.name.key, sa.VARCHAR(length=255), nullable=False),
    )
    op.create_index(Thing.INDEX_WORKSPACE_ID, Thing.__tablename__, [Thing.workspace_id.key])


def downgrade():
    op.drop_table(Thing.__tablename__)
```

## Rules to enforce (§11)

- **Reference the entity, not literals** — `Thing.__tablename__`,
  `Thing.id.key`, and the entity's `INDEX_*` / `UQ_*` class constants. The
  index name then exists in exactly one place (entity + migration agree).
- **No `alembic.ini`; no `alembic -c` CLI invocation** — go through the lib's
  `install()` / `uninstall()`.
- **One migration while unreleased** — fold changes into `_1_create_db.py`.
- `revision` / `down_revision` are stringified integers; update `.migration_ver`.
- Every `upgrade()` has a matching `downgrade()`.
- Never commit `.coverage` or build artifacts alongside the migration.

Create or change the entity first with the `core-lib-entity` skill.
