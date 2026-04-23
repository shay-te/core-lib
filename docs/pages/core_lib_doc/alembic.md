---
id: alembic
title: Alembic
sidebar: core_lib_doc_sidebar
permalink: alembic.html
folder: core_lib_doc
toc: false
---

Without schema migration tooling, changing a database schema in production means manually running SQL, coordinating across teammates, and hoping nothing breaks. `Alembic` integration in Core-Lib automates this — generate migration files, upgrade to the latest schema, roll back to a previous version — all from config, no raw SQL.

*core_lib.alembic.alembic.Alembic* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/alembic/alembic.py#L16){:target="_blank"}

Wraps [SQLAlchemy's Alembic tool](https://alembic.sqlalchemy.org/en/latest/){:target="_blank"} with Core-Lib's config pattern.

## Initializing

```python
def __init__(self, core_lib_path: str, core_lib_config: DictConfig):
```

**Arguments**

- **`core_lib_path`** *`(str)`*: Path of the `Core-Lib` main class file.
- **`core_lib_config`** *`(DictConfig)`*: Entire config of the `Core-Lib`.

**Configuration**

This section in the config YAML holds all the configurations for the Alembic. You can override your values in your specific `Core-Lib` config file.
For more information, you can check the official documentation [here](https://alembic.sqlalchemy.org/en/latest/tutorial.html#editing-the-ini-file){:target="_blank"}.

> `script_location` property must be set to the location where the migration folder exists.

> `version_table` property specifies the version tables to be created at the migrations, changing this value will assure that the tables don't create a conflict.

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
class YourCoreLib(CoreLib):
    .
    .
    .
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

This function will carry out the upgrade revisions of the alembic.

```python
def upgrade(self, revision: str = "head"):
```

**Arguments**

- **`revision`** *`(str)`*: Default `head`, The revision to which you want to upgrade e.g., '+1', '+2', etc.

### downgrade()

*core_lib.alembic.alembic.Alembic.downgrade()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/alembic/alembic.py#L75){:target="_blank"}

This function will carry out the downgrade revisions of the alembic.

```python
def downgrade(self, revision: str = "base"):
```

**Arguments**

- **`revision`** *`(str)`*: Default `base`, The revision to which you want to downgrade e.g., '1', '2', etc.

### history()

*core_lib.alembic.alembic.Alembic.history()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/alembic/alembic.py#L78){:target="_blank"}

This function returns the history of the revisions carried out.

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

Will create a migration with the provided name.

```python
def create_migration(self, migration_name):
```

**Arguments**

- **`migration_name`**: Name of the migration to create.

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/data_layers.html"><< Previous</a></button>
    <button class="pageNext-btn"><a href="/crud.html">Next >></a></button>
</div>