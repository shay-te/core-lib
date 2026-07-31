---
name: core-lib-migration
description: MANDATORY — load this skill BEFORE you add a migration or alter/create/drop any table, column, index, or constraint in a *-core-lib, and right after changing an entity; do not write it from memory. Creates an Alembic revision under data_layers/data/db/migrations/versions/ with matching upgrade/downgrade and sa.INTEGER. The model class itself is core-lib-entity.
---

# Create a core-lib migration (Alembic)

Each core-lib keeps Alembic migrations under
`<name>_core_lib/data_layers/data/db/migrations/versions/`. A migration **pins
the physical DDL at the moment it was written** and must not drift when the
entity later changes — so it is the one place where literal column-name strings
are correct.

## Steps

1. Make the entity change first (use `core-lib-entity`).
2. Generate the revision (autogenerate compares entity metadata to the DB):
   ```bash
   alembic -c <path-to-alembic.ini-or-hydra-config> revision --autogenerate -m "add widget status"
   ```
   If the repo wires Alembic through the main class
   (`CoreLib.install(cfg)` → `Alembic(...).upgrade()`), follow that repo's
   documented invocation instead.
3. Review the generated `upgrade()` / `downgrade()` — autogenerate misses
   server defaults, enum changes, and some index/constraint edits. Fix by hand.
4. Use `sa.INTEGER()` (not `sa.Integer()`).
5. Apply: `alembic upgrade head`.

## Canonical revision shape

```python
"""add widget status

Revision ID: 2026_06_24_widget_status
Revises: <down_revision>
"""
import sqlalchemy as sa
from alembic import op

revision = '2026_06_24_widget_status'
down_revision = '<previous_revision>'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('widget', sa.Column('status', sa.INTEGER(), nullable=False))


def downgrade():
    op.drop_column('widget', 'status')
```

## Rules to enforce (from AGENTS.md)

- **`sa.INTEGER()`, not `sa.Integer()`** (§3.5).
- **Literal column-name strings are correct here** — a migration is the
  documented exception to "names come from the entity"; it must not drift with
  the entity (§3.4).
- Every `upgrade()` has a matching `downgrade()`.
- Don't hand-edit an already-applied/published revision — add a new one.
- Never commit `.coverage` or build artifacts alongside the migration.
