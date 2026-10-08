---
id: migrations
title: Migrations
sidebar: core_lib_doc_sidebar
permalink: migrations.html
folder: core_lib_doc
toc: false
---

`core_lib migrate` creates and runs Alembic migrations from the command line. It is a front end to Core-Lib's [`Alembic` class](alembic.html): same config, same numbered revision files. Use it to add a revision and to move a database up or down, locally, in CI, or in a deploy step.

> **Where it fits:** Database schema management. After you change SQLAlchemy entities under `data_layers/data/db/`, create a revision and write the schema change in it by hand: the command does not compare your entities with the database.

## Before you run it

- Run it from your project root. That folder must contain `core_lib_config.yaml`, which composes Core-Lib's config with yours and names your package (a project made with `core_lib generate` has it):

  ```yaml
  defaults:
    - _self_
    - core_lib
    - your_core_lib

  core_lib_module: your_core_lib

  hydra:
    run:
      dir: .
  ```

  Without this file the command fails with `MissingConfigException: Cannot find primary config 'core_lib_config.yaml'`. `core_lib_module` is the package folder, relative to the project root, that holds `data_layers/`.
- The database it migrates is `core_lib.data.sqlalchemy.config.url` in that config. See [Which database is migrated](alembic.html#which-database-is-migrated).
- Environment variables are loaded from `.env` in the current folder, if it exists. Use `--env_file path/to/file` to load another file.

## Create a new migration

```bash
core_lib migrate --rev new --name create_db
```

`--rev new` creates a new revision and `--name` names it (`--name` is required here). The file goes into the `versions/` folder of your migrations folder (`script_location`, `data_layers/data/db/migrations/` by default). Revisions are numbered `1`, `2`, `3`, and the date comes first:

```text
your_core_lib/data_layers/data/db/migrations/versions/2026-05-15_1_create_db.py
```

The new file has empty `upgrade()` and `downgrade()` functions. Fill them in with Alembic `op.*` calls, as in the [example revision](alembic.html#example).

## Upgrade or downgrade

```bash
core_lib migrate --rev head
```

`--rev` accepts:

- `head`: upgrade to the latest migration
- `base`: downgrade all the way back
- `+1` ... `+10`: upgrade by N migrations
- `-1` ... `-10`: downgrade by N migrations
- `1` ... `10`: also upgrade by N migrations. `--rev 2` means "two steps up", not "to revision 2".

The CLI does not enforce the -10..10 range: any integer is passed to Alembic as a relative step, and `0`, or a step larger than the number of revisions available, raises `CommandError`. Any other value (not an integer, `head`, `base` or `new`) does nothing. To go to a specific revision number, call `Alembic(...).upgrade('2')` from Python (see [Alembic Migrations](alembic.html)).

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="rules_validator.html">Previous</a></button>
    <button class="pageNext-btn"><a href="generation.html">Next</a></button>
</div>
