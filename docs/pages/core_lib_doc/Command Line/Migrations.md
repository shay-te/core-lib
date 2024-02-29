---
id: migrations
title: Migrations
sidebar: core_lib_doc_sidebar
permalink: migrations.html
folder: core_lib_doc
toc: false
---

## Commands for **`Alembic`** migrations

### New Migration

### Command
```python
core_lib rev -n create_db
```

`rev -n` suggests new migration and the parameter after that will expect a name for the migration.

### Outcome

This command will create a new migration with the name `create_db`.

### Upgrade or Downgrade migrations

### Command
```python
core_lib rev -m head
```

`rev -m` suggests an existing migration and the parameter after that will expect the type of migration.

- `head`
- `base`
- `+1`, `+2` ..., `+10` : Mirgation upgrade versions
- `-1`, `-2` ..., `-10` : Mirgation downgrade versions

### Outcome

This command will migrate to the specified version in the last parameter of the command.

### Upgrade or Downgrade migrations

### Command
```python
core_lib rev -l
```

`rev -l` for listing the migration history.

### Outcome

This command will list the migration history in a list format.

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/rules_validator.html"><< Previous</a></button>
    <button class="pageNext-btn"><a href="/generation.html">Next >></a></button>
</div>