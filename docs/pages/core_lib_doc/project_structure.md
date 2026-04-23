---
id: project_structure
title: Project Structure
sidebar: core_lib_doc_sidebar
permalink: project_structure.html
folder: core_lib_doc
toc: false
---

Every `CoreLib` project follows the same folder structure. New team member? They know where everything lives immediately.

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

Each directory has a single responsibility:

- `service/` — business logic and orchestration
- `data_access/` — database queries, nothing else
- `data/` — ORM models, migrations, low-level definitions
- `client/` — external APIs and third-party services
- `jobs/` — background and scheduled tasks
- `your_core_lib.py` — wires everything together at startup

This mirrors the Core-Lib architecture directly: services don't know about infrastructure, data access doesn't know about business rules, and everything is wired in one place.

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
