---
id: alembic
title: Alembic
sidebar: core_lib_doc_sidebar
permalink: alembic.html
folder: core_lib_doc
toc: false
---

# Alembic

*core_lib.alembic.alembic.Alembic* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/alembic/alembic.py#L16){:target="_blank"}

This class provides functions that wrap the [Sqlalchemy's Alembic tool](https://alembic.sqlalchemy.org/en/latest/){:target="_blank"}.

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

`core_lib.yaml`

*core_lib.config.core_lib.yaml* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/config/core_lib.yaml#L33){:target="_blank"} 

`Core-Lib` default configuration.

```yaml
.
.
.
alembic:
    version_table: alembic_version
    sqlalchemy.url: ${core_lib.data}
    # A generic, single database configuration.

    # path to migration scripts
    script_location: data_layers/data/db/migrations

    # template used to generate migration files
    file_template:  "%%(year)d-%%(month).2d-%%(day).2d_%%(rev)s_%%(slug)s"

    # timezone to use when rendering the date
    # within the migration file as well as the filename.
    # string value is passed to dateutil.tz.gettz()
    # leave blank for localtime
    timezone: ~

    # max length of characters to apply to the
    # "slug" field
    truncate_slug_length: ~

    # set to 'true' to run the environment during
    # the 'revision' command, regardless of autogenerate
    revision_environment: false

    # set to 'true' to allow .pyc and .pyo files without
    # a source .py file to be detected as revisions in the
    # versions/ directory
    sourceless: false

    # version location specification; this defaults
    # to alembic/versions.  When using multiple version
    # directories, initial revisions must be specified with --version-path
    # version_locations: %(here)s/bar %(here)s/bat alembic/versions

    # the output encoding used when revision files
    # are written from script.py.mako
    output_encoding: utf-8

    post_write_hooks:
    # post_write_hooks defines scripts or Python functions that are run
    # on newly generated revision scripts.  See the documentation for further
    # detail and examples

    # format using "black" - use the console_scripts runner, against the "black" entrypoint
    # hooks=black
    # black.type=console_scripts
    # black.entrypoint=black
    # black.options=-l 79

    # Logging configuration
    logger:
      keys: root,sqlalchemy,alembic

      handlers:
        keys: console

      formatters:
        generic:
          format: "%(levelname)-5.5s %(name)s %(message)s"
          datefmt: "%H:%M:%S"

      loggers:
        root:
          level: WARN
          handlers: console
          qualname: ~

        sqlalchemy:
          level: WARN
          handlers: ~
          qualname: sqlalchemy.engine

        alembic:
          level: INFO
          handlers: ~
          qualname: alembic

        console:
          class: StreamHandler
          args: (sys.stderr,)
          level: NOTSET
          formatter: generic

    version_file_name: '.migration_ver'
    render_as_batch: false
```

`your_core_lib.yaml`

Config to override the original `Core-Lib` config.

```yaml
.
.
.
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