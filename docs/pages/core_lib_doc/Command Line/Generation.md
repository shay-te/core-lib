---
id: generation
title: Generation
sidebar: core_lib_doc_sidebar
permalink: generation.html
folder: core_lib_doc
toc: false
---

Setting up a new `CoreLib` by hand means creating about 20 files in the right folders, with the right base classes. `core_lib generate` reads a YAML description of your connections, entities, data access classes, services, caches and jobs, and writes a starter project with those files in place.

> **Where it fits:** Project setup. The generator creates the folders and starter classes for the six-layer structure; after generation, you fill in your domain logic.

> Don't change the YAML's top-level structure — `core_lib generate` reads specific keys. You can freely add or remove entities, data accesses, and other items inside the layers.

## Generate from a YAML file

```bash
core_lib generate --yaml "$(pwd)/ExampleCoreLib.yaml"
```

Pass the YAML's absolute path; `$(pwd)/` builds it for a file in the current folder. Run the command from the folder where the new project should go: the project is written to the current folder. If you omit `--yaml`, the command asks you questions, writes the YAML to the current folder, and then generates from it.

For a sample input, copy [`core_lib_generator/ExampleCoreLib.yaml`](https://github.com/shay-te/core-lib/blob/master/core_lib_generator/ExampleCoreLib.yaml){:target="_blank"} from the Core-Lib repository and edit it. Its top-level keys, all under `core_lib:`, are:

| Key | What it becomes |
|---|---|
| `name` | The `CoreLib` class name. `ExampleCoreLib` gives the class `ExampleCoreLib` in the package `example_core_lib`. |
| `env` | Values written to `.env`, for the `${oc.env:...}` variables in your config. |
| `connections` | One connection per entry (SQLAlchemy, Solr, Neo4j and others), in the generated config and `__init__`. |
| `caches` | A cache handler per entry, registered in `__init__`. |
| `jobs` | A `Job` class per entry in `jobs/`, and its settings in the generated config. |
| `entities` | One SQLAlchemy entity per entry, in `data_layers/data/<connection key>/entities/`. |
| `data_accesses` | One `DataAccess` class per entry. |
| `services` | One `Service` class per entry. |
| `setup` | The fields of `setup.py`. |

This YAML is input for the generator, not your app's config. For example, `jobs` here is a list with a `key` per job; the generator turns it into the mapping by job name that `load_jobs()` reads (see [Job](job.html)).

## What it creates

Generating from `ExampleCoreLib.yaml` creates:

```text
example_core_lib/                         # the project folder
├── example_core_lib/                     # the Python package
│   ├── config/
│   │   └── example_core_lib.yaml         # connections, caches and jobs
│   ├── data_layers/
│   │   ├── data/
│   │   │   └── sqlconn/                  # one folder per connection, named after its key
│   │   │       └── entities/
│   │   │           └── details.py
│   │   ├── data_access/
│   │   │   ├── details_data_access.py
│   │   │   ├── neo4j_data_access.py
│   │   │   └── solr_data_access.py
│   │   └── service/
│   │       └── details_service.py
│   ├── jobs/
│   │   └── update_user.py
│   └── example_core_lib.py               # ExampleCoreLib: the wiring
├── hydra_plugins/
│   └── example_core_lib/
│       └── example_core_lib_searchpath.py
├── tests/
│   ├── test_example_core_lib.py
│   └── test_data/
│       ├── helpers/
│       │   └── util.py
│       └── test_config/
│           ├── config.yaml
│           └── example_core_lib_override.yaml
├── example_core_lib_instance.py          # holds the one ExampleCoreLib of the process
├── core_lib_config.yaml                  # config the core_lib command loads, e.g. for migrations
├── .env
├── setup.py
├── requirements.txt
├── README.md
└── AGENTS.md
```

It also writes `__init__.py` files, `.gitignore`, `.dockerignore`, `MANIFEST.in` and a license file. There is no `client/` folder; add one when you need an external API. See [Project Structure](project_structure.html) for what each folder is for.

The output is a starting point, not a finished app. Read the generated classes before you build on them. The files under `tests/` are placeholders: fill in the test config and the test before you run them (see [Testing Core-Lib](test_core_lib.html)).

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="migrations.html">Previous</a></button>
    <button class="pageNext-btn"><a href="cache.html">Next</a></button>
</div>
