---
id: core_lib_main
title: Core Lib Main
sidebar_label: Core Lib Main
---

This file is the single gateway to interact with the `Core-Lib` Generator. It has functions to handle the creation of `Core-Lib` Yaml, generation of `Core-Lib` and handling migrations using the command line.


## Create a new Core-Lib YAML file 

### Command

```python
core_lib -c
```

This command will take user input for various `Core-Lib` configurations and details necessary for generating the `Core-Lib` like:
- `Core-Lib` Name
- `DB Connection` config and details.
- `DB Entities` config and details.
- `DataAccess` config and details.
- `Cache` config and details.
- `Jobs` config and details.
- `setup.py` details

You can have multiple `DB connections`, `DB entities`, `DataAccess`, `Cache` connections and `Jobs`. 

> Please when inserting names for various properties please follow the naming convention i.e. for class names use `PascalCase` for entity name use `snake_case`

### Outcome

Once you fill out all the necessary information a Yaml file will be generated with the `Core-Lib` name provided by you at the location from which you ran the command. For e.g. `ConversationCoreLib.yaml`

`ExampleCoreLib.yaml`

```yaml
core_lib:
  name: ExampleCoreLib
  env:
    USERDB_DB: userdb
    USERDB_USER: user
    USERDB_PASSWORD: password
    USERDB_PORT: 5432
    USERDB_HOST: localhost
    REDISCACHE_PORT: 6379
    REDISCACHE_HOST: localhost
  connections:
  - key: userdb
    migrate: true
    log_queries: false
    create_db: true
    session:
      pool_recycle: 3200
      pool_pre_ping: false
    url:
      file: ${oc.env:USERDB_DB}
      protocol: postgresql
      username: ${oc.env:USERDB_USER}
      password: ${oc.env:USERDB_PASSWORD}
      port: ${oc.env:USERDB_PORT}
      host: ${oc.env:USERDB_HOST}
  - key: sellerdb
    migrate: true
    log_queries: false
    create_db: true
    session:
      pool_recycle: 3200
      pool_pre_ping: false
    url:
      protocol: sqlite
  caches:
  - key: memorycache
    type: memory
  - key: rediscache
    type: redis
    url:
      host: ${oc.env:REDISCACHE_HOST}
      port: ${oc.env:REDISCACHE_PORT}
      protocol: redis
  jobs:
  - key: update_user
    initial_delay: 0s
    frequency: ''
    handler:
      _target_: example_core_lib.example_core_lib.jobs.update_user.UpdateUser
  entities:
  - key: details
    db_connection: userdb
    columns:
    - key: username
      type: VARCHAR
      default: ''''''
      nullable: true
    - key: password
      type: VARCHAR
      default: ''''''
      nullable: true
    - key: active
      type: BOOLEAN
      default: false
      nullable: true
    is_soft_delete: true
    is_soft_delete_token: true
  - key: details
    db_connection: sellerdb
    columns:
    - key: username
      type: VARCHAR
      default: ''''''
      nullable: false
    - key: password
      type: VARCHAR
      default: null
      nullable: true
    - key: active
      type: BOOLEAN
      default: false
      nullable: false
    is_soft_delete: true
    is_soft_delete_token: false
  - key: data
    db_connection: sellerdb
    columns:
    - key: address
      type: VARCHAR
      default: null
      nullable: true
    is_soft_delete: false
    is_soft_delete_token: false
  data_accesses:
  - key: DetailsDataAccess
    entity: details
    db_connection: userdb
    is_crud: true
    is_crud_soft_delete: true
    is_crud_soft_delete_token: true
  - key: SellerDetailsDataAccess
    entity: details
    db_connection: sellerdb
    is_crud: true
    is_crud_soft_delete: true
  - key: DataDataAccess
    entity: data
    db_connection: sellerdb
  setup:
    author: name
    author_email: name@name.com
    description: Project
    url: ''
    license: MIT
    classifiers:
    - 'Development Status :: 3 - Alpha'
    - 'Development Status :: 4 - Beta'
    - 'Development Status :: 5 - Production/Stable'
    - 'Environment :: MacOS X'
    - 'Environment :: Win32 (MS Windows)'
    - 'Framework :: Django :: 4.0'
    version: 0.0.0.1
```

This file will contain all the data inserted by you in a structured format which is highly editable properties.

> Please don't change the structure of the Yaml data as this file is responsible for generating the `Core-Lib`, you can add or remove any Entity, DataAccess or any other items inside other layers.

## Generate a new Core-Lib from the YAML file 

### Command

```python
core_lib -g ExampleCoreLib.yaml
```

Run this command where the Yaml file is located or re-locate the file to a location where you want to create the `Core-Lib`.

### Outcome

A folder by the `Core-Lib` name will be created and inside the folder will be your `Core-Lib`!

Now that you have the `Core-Lib` you can initialize it and use it directly or integrate it with your current application.

> Please read the documents to understand what each file does and understand `Core-Lib` more throughly.

## Migrations

Commands for `Alembic` migrations

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