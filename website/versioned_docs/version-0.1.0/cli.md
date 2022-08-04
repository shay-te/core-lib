---
id: cli
title: Command Line
sidebar_label: Command Line
---

`core_lib_main` is the single gateway to interact with `Core-Lib` using the command line.  
It offers the following tools:

- Generating `Core-Lib` from YAML will create a `Core-Lib` folder with your `Core-Lib` inside.
- Run Migration, `Alembic` upgrade, or downgrade for migrations.
- List Migrations created until now.


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