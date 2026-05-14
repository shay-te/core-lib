---
id: migrations
title: Migrations
sidebar: core_lib_doc_sidebar
permalink: migrations.html
folder: core_lib_doc
toc: false
---

Schema changes in production are risky when run manually — wrong order, forgotten step, no rollback path. Core-Lib's `core_lib migrate` command wraps Alembic so every migration is a versioned, reversible step that runs the same way locally, in CI, and in production.

> **Where it fits:** Database schema management. Use this after changing SQLAlchemy entities under `data_layers/data/db/`.

## Create a new migration

```bash
core_lib migrate --rev new --name create_db
```

`--rev new` creates a new migration revision. `--name` sets the migration name. The command creates a new migration file named `create_db` in your `data_layers/data/db/migrations/` folder.

Example generated file path:

```text
data_layers/data/db/migrations/2026-05-15_ab12cd_create_db.py
```

## Upgrade or downgrade

```bash
core_lib migrate --rev head
```

`--rev` accepts any of the following:

- `head` — upgrade to the latest migration
- `base` — downgrade all the way back
- `+1`, `+2` ..., `+10` — upgrade by N versions
- `-1`, `-2` ..., `-10` — downgrade by N versions

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/rules_validator.html">Previous</a></button>
    <button class="pageNext-btn"><a href="/generation.html">Next</a></button>
</div>
