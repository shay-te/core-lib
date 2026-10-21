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

## Create and run revisions with `core_lib migrate` (docs: *Migrations*)

From the project root (it needs `core_lib_config.yaml`, which composes `core_lib` with your lib and
sets `core_lib_module`):

- `core_lib migrate --rev new --name create_db` — writes an EMPTY numbered revision
  (`versions/<date>_<N>_create_db.py`) and updates `.migration_ver`. There is no autogenerate: you
  write `upgrade()`/`downgrade()` yourself, in the shape below.
- `core_lib migrate --rev head` / `base` / `+N` / `-N` — move the database. A bare `2` means "two
  steps up", not "to revision 2".

## ⛔ Which database is migrated — the silent trap

`Alembic` always migrates **`core_lib.data.sqlalchemy.config.url`**. If your lib keeps its connection
anywhere else, that path keeps Core-Lib's default — an in-memory SQLite database — and the migration
"succeeds" against it with no error, leaving the real database untouched. Keep the DB block at
`core_lib.data.sqlalchemy` (§3.1), or point that `url` at yours with an interpolation. Overrides of
the `alembic` section go under `core_lib.alembic` (a top-level `alembic:` key is ignored), and
`script_location` must be relative to the package folder.

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
  `Thing.id.key`, and the entity's `INDEX_*` class constants. The
  index name then exists in exactly one place (entity + migration agree).
- A unique key is `op.create_index(Thing.INDEX_X, Thing.__tablename__, [...],
  unique=True)`, never `sa.UniqueConstraint` (see `core-lib-entity`).
- **No `alembic.ini`; no `alembic -c` CLI invocation** — go through the lib's
  `install()` / `uninstall()` or `core_lib migrate`.
- **One migration while unreleased** — fold changes into `_1_create_db.py`.
- `revision` / `down_revision` are stringified integers; update `.migration_ver`.
- Every `upgrade()` has a matching `downgrade()`; `downgrade()` drops children before parents, and
  `upgrade()` creates parents first.
- **Mixin columns are spelled out per table**, after the business columns: `created_at`,
  `updated_at`, `deleted_at`, and `deleted_at_token` for token entities (§11.3).
- **Verify the revision against the entities**: run it and `Base.metadata.create_all` on two fresh
  SQLite databases and diff the reflected schemas (tables, columns, types, nullability, defaults,
  indexes, uniques). Any drift means the migration or the entity is wrong (§11.3).
- Never commit `.coverage` or build artifacts alongside the migration.
- **Test it on a SQLite FILE, never `:memory:`** — Alembic opens its own engine.
  `build_url` strips a leading `/`, so pass `os.path.relpath(path)`; compare the
  migrated schema with `create_all` on a second file.
- **`MANIFEST.in` ships the migration templates** —
  `recursive-include foo_core_lib/data_layers/data/db/migrations *.mako .migration_ver`,
  or an installed wheel cannot run `install()` (§14).

Create or change the entity first with the `core-lib-entity` skill.
