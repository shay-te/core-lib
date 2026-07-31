---
name: core-lib-entity
description: MANDATORY — load this skill BEFORE you add or change any table, model, ORM class, entity, column, field, or nested enum in a *-core-lib; do not write it from memory. Creates one SQLAlchemy entity (Data layer) under data_layers/data/db/entities/ on Base, soft-delete mixins, INTEGER, IntEnum. Pair with core-lib-migration (DDL) and core-lib-data-access (queries).
---

The canonical, tool-neutral version of this skill lives at
[`skills/core-lib-entity/SKILL.md`](../../../skills/core-lib-entity/SKILL.md)
(kept tool-neutral so non-Claude agents can use it too). **Read that file and
follow it.**
