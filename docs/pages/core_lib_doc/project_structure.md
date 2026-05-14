---
id: project_structure
title: Project Structure
sidebar: core_lib_doc_sidebar
permalink: project_structure.html
folder: core_lib_doc
toc: false
---

Every `CoreLib` project follows the same folder structure. The folders map directly onto the six layers from the [home page](/index.html#the-layers) — new team member, same folders, no surprises.

```
your_core_lib/
├── your_core_lib/
│   ├── config/
│   │   └── your_core_lib.yaml      # infrastructure wiring
│   ├── data_layers/
│   │   ├── data/
│   │   │   ├── db/                 # ORM models
│   │   │   │   └── migrations/
│   │   │   ├── elastic/            # Elasticsearch mappings
│   │   │   └── mongo/              # MongoDB schemas
│   │   ├── data_access/            # database query APIs
│   │   │   └── user/
│   │   │       ├── user_data_access.py
│   │   │       └── user_list_data_access.py
│   │   └── service/                # business logic
│   │       └── user/
│   │           ├── user_service.py
│   │           └── user_list_service.py
│   ├── client/                     # external APIs
│   │   └── stripe_client.py
│   ├── jobs/                       # background tasks
│   │   └── sync_users_job.py
│   └── your_core_lib.py            # wiring — the single entry point
└── tests/
    └── config/
        └── test_config.yaml        # SQLite + mock clients override
```

---

## How to think about it

Each directory holds one layer from the index table — and nothing else.

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

---

## `your_core_lib.py`

This is your `CoreLib` implementation — the entry point of your application. All dependencies (DB connections, clients, caches) are created here and injected into services. Nothing else creates them.

---

## Config

All infrastructure is configured in `your_core_lib.yaml`. This is what lets you:

- swap databases, clients, or services without touching business logic
- run the same code with different wiring for dev, test, and production

Test config overrides only what differs — typically just swapping Postgres for SQLite and real clients for mocks.

---

## Why this structure

Most projects become inconsistent over time — business logic leaks into data layers, services start importing frameworks, dependencies spread across files.

This structure prevents that by enforcing clear boundaries from the start. If you don't know where a file belongs, that's usually a sign the responsibility needs to be clarified.

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/advantages.html"><< Previous</a></button>
    <button class="pageNext-btn"><a href="/core_lib_main_class.html">Next >></a></button>
</div>
