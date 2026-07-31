---
name: core-lib-migration
description: MANDATORY — load this skill BEFORE you add a migration or alter/create/drop any table, column, index, or constraint in a *-core-lib, and right after changing an entity; do not write it from memory. Creates an Alembic revision under data_layers/data/db/migrations/versions/ with matching upgrade/downgrade and sa.INTEGER. The model class itself is core-lib-entity.
---

The canonical, tool-neutral version of this skill lives at
[`skills/core-lib-migration/SKILL.md`](../../../skills/core-lib-migration/SKILL.md)
(kept tool-neutral so non-Claude agents can use it too). **Read that file and
follow it.**
