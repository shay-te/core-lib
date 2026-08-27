---
id: alembic
title: Alembic Migrations
sidebar: core_lib_doc_sidebar
permalink: alembic.html
folder: core_lib_doc
toc: false
---

Without schema migration tooling, changing a database schema in production means manually running SQL, coordinating across teammates, and hoping nothing breaks. `Alembic` integration in Core-Lib automates this — generate migration files, upgrade to the latest schema, roll back to a previous version — all from config, no raw SQL.

*core_lib.alembic.alembic.Alembic* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/alembic/alembic.py#L16){:target="_blank"}

Wraps [Alembic](https://alembic.sqlalchemy.org/en/latest/){:target="_blank"} with Core-Lib's config pattern.

> **Where it fits:** DataAccess-layer support. Run at startup or in CI to bring the database schema up to date with the entities defined under `data_layers/data/db/`.

## Initializing

```python
def __init__(self, core_lib_path: str, core_lib_config: DictConfig):
```

**Arguments**

- **`core_lib_path`** *`(str)`*: Path to the Core-Lib main class file.
- **`core_lib_config`** *`(DictConfig)`*: Full Core-Lib config.

**Configuration**

The `alembic` section in YAML configures migration behavior. Override only the values that differ for your app.

> `script_location` must point to the folder that contains your migration files.

> `version_table` controls where Alembic stores migration state. Change it when multiple Core-Libs share one database.

`core_lib.yaml` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/config/core_lib.yaml#L33){:target="_blank"}

The default Alembic configuration baked into Core-Lib. The two properties you'll typically override are:

- **`script_location`** — path to your migrations folder
- **`version_table`** — avoids conflicts when multiple Core-Libs share a database

```yaml
alembic:
    version_table: alembic_version
    sqlalchemy.url: ${core_lib.data}
    script_location: data_layers/data/db/migrations
    file_template: "%%(year)d-%%(month).2d-%%(day).2d_%%(rev)s_%%(slug)s"
    version_file_name: '.migration_ver'
    render_as_batch: false
```

`your_core_lib.yaml` — override only what differs:

```yaml
alembic:
    version_table: example_alembic_version
    script_location: data_layers/data/user_db/migrations
```

**Example**

```python
import os
import inspect
from omegaconf import DictConfig
from core_lib.alembic.alembic import Alembic


class YourCoreLib(CoreLib):
    ...

    @staticmethod
    def install(cfg: DictConfig):
        Alembic(os.path.dirname(inspect.getfile(YourCoreLib)), cfg).upgrade()

    @staticmethod
    def uninstall(cfg: DictConfig):
        Alembic(os.path.dirname(inspect.getfile(YourCoreLib)), cfg).downgrade()
```

## Functions

### upgrade()

*core_lib.alembic.alembic.Alembic.upgrade()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/alembic/alembic.py#L72){:target="_blank"}

Runs Alembic upgrade to the requested revision.

```python
def upgrade(self, revision: str = "head"):
```

**Arguments**

- **`revision`** *`(str)`*: Default `head`. Target revision, e.g. `+1`, `+2`, or `head`.

### downgrade()

*core_lib.alembic.alembic.Alembic.downgrade()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/alembic/alembic.py#L75){:target="_blank"}

Runs Alembic downgrade to the requested revision.

```python
def downgrade(self, revision: str = "base"):
```

**Arguments**

- **`revision`** *`(str)`*: Default `base`. Target revision, e.g. `-1`, `-2`, or `base`.

### history()

*core_lib.alembic.alembic.Alembic.history()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/alembic/alembic.py#L78){:target="_blank"}

Returns Alembic revision history.

```python
def history(self):
```

**Returns**

Returns the history of revisions.

```
INFO:core_lib.core_lib_main:revision to `list`
1 -> 2 (head), new_table
<base> -> 1, create_db
```

### create_migration()

*core_lib.alembic.alembic.Alembic.create_migration()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/alembic/alembic.py#L81){:target="_blank"}

Creates a migration with the provided name.

```python
def create_migration(self, migration_name):
```

**Arguments**

- **`migration_name`**: Name of the migration to create.

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/data_layers.html">Previous</a></button>
    <button class="pageNext-btn"><a href="/crud.html">Next</a></button>
</div>
