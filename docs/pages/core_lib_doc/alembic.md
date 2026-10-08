---
id: alembic
title: Alembic Migrations
sidebar: core_lib_doc_sidebar
permalink: alembic.html
folder: core_lib_doc
toc: false
---

`Alembic` (`core_lib.alembic.alembic.Alembic`) runs [Alembic](https://alembic.sqlalchemy.org/en/latest/){:target="_blank"} schema migrations using your Core-Lib config. Call it from your `CoreLib`'s `install()` and `uninstall()`, or use the [`core_lib migrate`](migrations.html) command, which uses the same class.

What it adds over running Alembic yourself:

- No `alembic.ini` and no `env.py` to set up: the database URL and the migrations folder come from the same YAML config as your app.
- Revisions are numbered `1`, `2`, `3`, and files are named `<date>_<number>_<name>.py`, for example `2026-05-15_1_create_db.py`.
- Each library can set its own `version_table`, so several Core-Lib libraries keep separate migration histories in one database.

It does not write migrations for you. `create_migration()` creates an empty, numbered revision, and you write its `upgrade()` and `downgrade()` with Alembic `op.*` calls. It does not compare your entities with the database (there is no autogenerate).

> **Where it fits:** Database schema management, outside the request path. Nothing runs it automatically: call `install()` from a deploy script or test setup, or run `core_lib migrate`.

*core_lib.alembic.alembic.Alembic* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/alembic/alembic.py#L16){:target="_blank"}

## Initializing

```python
def __init__(self, core_lib_path: str, core_lib_config: DictConfig):
```

**Arguments**

- **`core_lib_path`** *`(str)`*: The directory of your Core-Lib package, the folder that contains `data_layers/`. `script_location` is resolved relative to it. Usually `os.path.dirname(inspect.getfile(YourCoreLib))`. Passing the `.py` file instead of its folder fails with `ValueError: config.alembic.script_location dose not exists`.
- **`core_lib_config`** *`(DictConfig)`*: The full composed config. `Alembic` reads `core_lib.alembic` and `core_lib.data.sqlalchemy.config`.

## Configuration

### Which database is migrated

`Alembic` always migrates the database at **`core_lib.data.sqlalchemy.config.url`**, and logs SQL when `core_lib.data.sqlalchemy.config.log_queries` is true. It overwrites the `sqlalchemy.url` key of the `alembic` section with that URL.

If your library keeps its connection config somewhere else, point that path at it. A library made with `core_lib generate` keeps its connections under `core_lib.<your_core_lib>.data.<connection key>`. Without a line like the one below, `core_lib.data.sqlalchemy.config.url` keeps Core-Lib's default, an in-memory SQLite database, and the migration runs there without any error.

```yaml
# @package _global_
core_lib:
  data:
    sqlalchemy:
      config:
        url: ${core_lib.your_core_lib.data.userdb.url}   # the path of your connection's url block
```

### The `alembic` section

Core-Lib's defaults, under `core_lib.alembic` in `core_lib.yaml` [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/config/core_lib.yaml#L43){:target="_blank"} (shortened):

```yaml
core_lib:
  alembic:
    version_table: alembic_version
    sqlalchemy.url: ${core_lib.data}      # replaced at runtime, see above
    script_location: data_layers/data/db/migrations
    file_template: "%%(year)d-%%(month).2d-%%(day).2d_%%(rev)s_%%(slug)s"
    version_file_name: '.migration_ver'
    render_as_batch: false
```

Override only what differs, nested under `core_lib:` in your library's YAML. A top-level `alembic:` key is ignored.

```yaml
# @package _global_
core_lib:
  alembic:
    version_table: your_core_lib_alembic_version
    script_location: data_layers/data/user_db/migrations   # relative to core_lib_path
```

- **`version_table`**: the table where Alembic records the current revision. Give each library its own when several share a database.
- **`script_location`**: the migrations folder. It must be a relative path (relative to `core_lib_path`; an absolute path raises `ValueError`) and must exist. It holds Alembic's revision template, `script.py.mako`, and a `versions/` folder for the revision files. A project made with `core_lib generate` already has both.
- **`version_file_name`**: a file in the migrations folder where `create_migration()` writes the latest revision number.

## Example

```python
import os
import inspect
from omegaconf import DictConfig
from core_lib.alembic.alembic import Alembic
from core_lib.core_lib import CoreLib


class YourCoreLib(CoreLib):
    ...

    @staticmethod
    def install(cfg: DictConfig):
        Alembic(os.path.dirname(inspect.getfile(YourCoreLib)), cfg).upgrade()

    @staticmethod
    def uninstall(cfg: DictConfig):
        Alembic(os.path.dirname(inspect.getfile(YourCoreLib)), cfg).downgrade()
```

Nothing calls these for you. Call `YourCoreLib.install(cfg)` from your deploy script or test setup, or run `core_lib migrate --rev head` (see [Migrations](migrations.html)). `core_lib generate` adds both methods when you ask it for migrations.

A revision file, after you fill in the empty `upgrade()` and `downgrade()` that `create_migration('create_db')` wrote. It uses `User.__tablename__` and `User.email.key` instead of repeating the names as strings, so the table and column names are written once, in the entity:

```python
"""create_db

Revision ID: 1
Revises:
Create Date: 2026-05-15 10:26:43.183254

"""
from alembic import op
import sqlalchemy as sa

from your_core_lib.data_layers.data.db.entities.user import User


# revision identifiers, used by Alembic.
revision = '1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        User.__tablename__,
        sa.Column(User.id.key, sa.Integer, primary_key=True),
        sa.Column(User.email.key, sa.VARCHAR(255), nullable=False),
    )


def downgrade():
    op.drop_table(User.__tablename__)
```

## Functions

### upgrade()

*core_lib.alembic.alembic.Alembic.upgrade()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/alembic/alembic.py#L73){:target="_blank"}

Upgrades the database to the given revision.

```python
def upgrade(self, revision: str = "head"):
```

**Arguments**

- **`revision`** *`(str)`*: Default `head`. A revision number such as `'2'` (upgrade to revision 2), a relative step such as `'+1'`, or `'head'`.

### downgrade()

*core_lib.alembic.alembic.Alembic.downgrade()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/alembic/alembic.py#L77){:target="_blank"}

Downgrades the database to the given revision.

```python
def downgrade(self, revision: str = "base"):
```

**Arguments**

- **`revision`** *`(str)`*: Default `base` (undo every migration). A revision number such as `'1'`, a relative step such as `'-1'`, or `'base'`.

### history()

*core_lib.alembic.alembic.Alembic.history()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/alembic/alembic.py#L81){:target="_blank"}

Prints the revision history to stdout. Returns `None`.

```python
def history(self):
```

Example output:

```
1 -> 2 (head), add_user_name
<base> -> 1, create_db
```

### create_migration()

*core_lib.alembic.alembic.Alembic.create_migration()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/alembic/alembic.py#L84){:target="_blank"}

Creates `versions/<date>_<N>_<migration_name>.py` in the migrations folder, where `N` is the number of existing revisions plus one. The new file has empty `upgrade()` and `downgrade()` functions for you to fill in. It also writes `N` to the `version_file_name` file.

```python
def create_migration(self, migration_name):
```

**Arguments**

- **`migration_name`**: Name of the migration, used in the file name and the revision message. Must not be empty.

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="data_layers.html">Previous</a></button>
    <button class="pageNext-btn"><a href="crud.html">Next</a></button>
</div>
