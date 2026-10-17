---
id: project_structure
title: Project Structure
sidebar: core_lib_doc_sidebar
permalink: project_structure.html
folder: core_lib_doc
toc: false
---

This is the layout `core_lib generate` creates (see [Generation](generation.html)); you add the `client/` and `migrations/` folders when you need them. Following it in a hand-written project keeps it familiar to anyone who has seen another Core-Lib project. The folders map onto the six layers from the [home page](index.html#the-layers).

> **Where it fits:** Project map. Use this page when deciding where a new class or config file belongs.

```
your_core_lib/                         # the project (repository) folder
├── your_core_lib/                     # the Python package
│   ├── config/
│   │   └── your_core_lib.yaml         # infrastructure wiring: connections, caches, jobs
│   ├── data_layers/
│   │   ├── data/
│   │   │   └── db/                    # one folder per connection, named after its key
│   │   │       ├── entities/          # ORM models
│   │   │       │   └── user.py
│   │   │       └── migrations/        # Alembic scripts (add when needed, see Migrations)
│   │   ├── data_access/               # database query APIs
│   │   │   ├── user_data_access.py
│   │   │   └── user_list_data_access.py
│   │   └── service/                   # business logic
│   │       ├── user_service.py
│   │       └── user_list_service.py
│   ├── client/                        # external APIs (add this folder yourself)
│   │   └── stripe_client.py
│   ├── jobs/                          # background tasks
│   │   └── sync_users_job.py
│   └── your_core_lib.py               # the CoreLib subclass: builds and wires everything
├── hydra_plugins/
│   └── your_core_lib/
│       └── your_core_lib_searchpath.py  # lets Hydra find config/your_core_lib.yaml
├── tests/
│   ├── test_your_core_lib.py
│   └── test_data/
│       ├── helpers/
│       │   └── util.py                # builds one CoreLib for the whole test run
│       └── test_config/
│           ├── config.yaml            # the config tests load
│           └── your_core_lib_override.yaml  # what tests change: SQLite, mock clients
├── your_core_lib_instance.py          # holds the one CoreLib of this process
├── core_lib_config.yaml               # config the core_lib CLI loads (migrations)
├── requirements.txt
└── setup.py
```

The generator also writes a few packaging files (`README.md`, `.env`, `.gitignore`, `MANIFEST.in`, a license). The other pages in these docs keep test config in a shorter `tests/config/` folder; either works, because `load_core_lib_config()` takes a path relative to the test file (see [Testing Core-Lib](test_core_lib.html)).

---

## How to think about it

Each directory holds one layer from the [layer table](index.html#the-layers) on the home page — and nothing else.

| Folder | Layer | Holds |
|---|---|---|
| `your_core_lib.py` | `CoreLib` | Wiring — the single entry point. |
| `data_layers/service/` | `Service` | Business logic and orchestration. |
| `data_layers/data_access/` | `DataAccess` | Database queries, nothing else. |
| `data_layers/data/` | (entities) | ORM models, migrations, mappings. Used by `DataAccess`; not a public-facing layer. |
| `client/` | `Client` | HTTP / third-party API wrappers. |
| `jobs/` | `Job` | Background and scheduled tasks. |
| `config/` | — | YAML configs that decide which `Connection`, cache, and client classes get instantiated. |

`Connection` instances are constructed inside `your_core_lib.py` from the YAML — they don't get their own folder.

The files outside the package:

| File | What it is for |
|---|---|
| `your_core_lib_instance.py` | Holds the one `CoreLib` of the process: your entry point calls `init(config)` once, everything else calls `get()`. See [The CoreLib Class](core_lib_main_class.html#3-create-it-once-per-process). |
| `hydra_plugins/your_core_lib/` | Adds `pkg://your_core_lib.config` to Hydra's search path, so another config can list `your_core_lib` under `defaults:` once the package is installed. |
| `core_lib_config.yaml` | The config the `core_lib` command line tool loads, for example for `core_lib migrate` (see [Migrations](migrations.html)). |
| `tests/` | Tests that build the same `CoreLib` from a test config. See [Testing Core-Lib](test_core_lib.html). |

---

## `your_core_lib.py`

This is your `CoreLib` implementation — the entry point of your application. All dependencies (DB connections, clients, caches) are created here and passed into services. Nothing else should create them. [The CoreLib Class](core_lib_main_class.html) walks through writing it, loading its YAML and calling it from Flask and Django.

---

## Config

All infrastructure is configured in `your_core_lib.yaml`. This is what lets you:

- swap databases, clients, or services without touching business logic
- run the same code with different wiring for dev, test, and production

Test config (`tests/test_data/test_config/`) overrides only what differs — typically just swapping Postgres for SQLite and real clients for mocks.

---

## Why this structure

Most projects become inconsistent over time — business logic leaks into data layers, services start importing frameworks, dependencies spread across files.

This layout gives every kind of code one obvious home from the start, so a misplaced import stands out in review. It does not enforce anything by itself: Python will not stop a service from importing Flask. If you want that checked, add an import rule to CI (for example with import-linter). If you don't know where a file belongs, that's usually a sign the responsibility needs to be clarified.

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="advantages.html">Previous</a></button>
    <button class="pageNext-btn"><a href="glossary.html">Next</a></button>
</div>
