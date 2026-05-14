---
id: migrations
title: Migrations
sidebar: core_lib_doc_sidebar
permalink: migrations.html
folder: core_lib_doc
toc: false
---

Schema changes in production are risky when run manually — wrong order, forgotten step, no rollback path. Core-Lib's `core_lib migrate` command wraps Alembic so every migration is a versioned, reversible step that runs the same way locally, in CI, and in production.

## Commands for **`Alembic`** migrations

### New Migration

### Command
```bash
core_lib migrate --rev new --name create_db
```

`--rev new` creates a new migration revision. `--name` sets the migration name.

### Outcome

This command will create a new migration with the name `create_db`.

### Upgrade or Downgrade migrations

### Command
```bash
core_lib migrate --rev head
```

`--rev` accepts any of the following:

- `head` — upgrade to the latest migration
- `base` — downgrade all the way back
- `+1`, `+2` ..., `+10` — upgrade by N versions
- `-1`, `-2` ..., `-10` — downgrade by N versions

### Outcome

This command will migrate to the specified version.

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/rules_validator.html"><< Previous</a></button>
    <button class="pageNext-btn"><a href="/generation.html">Next >></a></button>
</div>