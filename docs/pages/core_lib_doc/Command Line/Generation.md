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
core_lib generate --yaml ExampleCoreLib.yaml
```

The YAML path may be relative to the current folder or absolute. Run the command from the folder where the new project should go: the project is written to the current folder. If the file does not exist, the command prints the path it looked for and exits with status 1. If you omit `--yaml`, the command asks you questions, writes the YAML to the current folder, and then generates from it.

The same YAML always generates the same files, line for line, so a regenerated project diffs cleanly against the last one.

For a sample input, copy [`core_lib_generator/ExampleCoreLib.yaml`](https://github.com/shay-te/core-lib/blob/master/core_lib_generator/ExampleCoreLib.yaml){:target="_blank"} from the Core-Lib repository and edit it. Its top-level keys, all under `core_lib:`, are:

| Key | What it becomes |
|---|---|
| `name` | The `CoreLib` class name. `ExampleCoreLib` gives the class `ExampleCoreLib` in the package `example_core_lib`. |
| `env` | Values written to `.env`, for the `${oc.env:...}` variables in your config. |
| `connections` | One connection per entry, in the generated config and `__init__`. Its `type` is `SqlAlchemyConnectionFactory`, `SolrConnectionFactory` or `Neo4jConnectionFactory` (full module path); any other type stops the generator with a `ValueError` that names it. |
| `caches` | A cache handler per entry, registered in `__init__`. Its `type` is `memory`, `memcached` or `redis`; any other type raises `ValueError`. A Memcached or Redis cache's `url` goes to `core_lib.<your_core_lib>.cache.<key>.url` in the generated config, where `__init__` reads it. |
| `jobs` | A `Job` class per entry in `jobs/`, and its settings in the generated config. |
| `entities` | One SQLAlchemy entity per entry, in `data_layers/data/<connection key>/entities/`. A column's `default` is written as given, `0`, `false` and `""` included; `null` means no default. |
| `data_accesses` | One `DataAccess` class per entry. Its base class comes from the first of `is_crud_soft_delete_token`, `is_crud_soft_delete` and `is_crud` that is `true`: `CRUDSoftDeleteWithTokenDataAccess`, `CRUDSoftDeleteDataAccess` or `CRUDDataAccess`. With all three `false` or left out, it is a plain `DataAccess`. A plain one without a `connection` is built with no arguments; a CRUD one needs a `connection`, and without it the generator stops with a `ValueError`. |
| `services` | One `Service` class per entry. |
| `setup` | The fields of `setup.py`. Its `license` is `MIT`, `APACHE_LICENSE_2` or `MOZILLA_PUBLIC_LICENSE_2`; any other value raises `ValueError`. |

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
├── requirements.txt                      # core-lib[neo4j,postgres,solr]: the extras your connections need
├── README.md
└── AGENTS.md                             # points AI coding agents at Core-Lib's rulebook and skills
```

`AGENTS.md` tells an AI coding agent to load the matching Core-Lib skill before it writes code, and says where to find the skills: in a `core-lib` checkout next to the project, or in the installed package's `agent_docs` folder (see [Built for AI coding agents](advantages.html#built-for-ai-coding-agents)).

`requirements.txt` names the [Core-Lib extras](index.html#installing) for the connections and caches in your YAML: `postgres` or `mysql` from a SQLAlchemy URL's `protocol`, `solr` and `neo4j` from the connection's `type`, `redis` and `memcached` from a cache's `type`. An SQLite-only project gets plain `core-lib`. Add `flask` or `django` yourself if the project serves web requests with Core-Lib's web helpers.

In the generated `ExampleCoreLib`, each service is a public attribute named after its class without `Service`: `DetailsService` becomes `example_core_lib.details`. Each data access class is private (`_details_data_access`), so routes, jobs and tests go through the services. A service whose short name `CoreLib` already uses, such as `ConfigService`, keeps its full name (`config_service`).

It also writes `__init__.py` files, `.gitignore`, `.dockerignore`, `MANIFEST.in` and a license file. There is no `client/` folder; add one when you need an external API. See [Project Structure](project_structure.html) for what each folder is for.

The output is a starting point, not a finished app. Read the generated classes before you build on them.

The generated tests run as they are: from the project folder, `python -m unittest discover -s tests -t .` builds your `CoreLib` once from `tests/test_data/test_config/config.yaml` and runs one empty test per service (per data access class if you declared no services). That config composes your library's YAML with `example_core_lib_override.yaml`, so the connections must be reachable from the test run. If they point at a Postgres server, Solr or Neo4j you do not have locally, override them there, for example with an SQLite `url`. Then replace the empty test methods with real ones (see [Testing Core-Lib](test_core_lib.html)).

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="migrations.html">Previous</a></button>
    <button class="pageNext-btn"><a href="cache.html">Next</a></button>
</div>
