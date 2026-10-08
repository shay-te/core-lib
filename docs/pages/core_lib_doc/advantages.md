---
id: advantages
title: Advantages
sidebar: core_lib_doc_sidebar
permalink: advantages.html
folder: core_lib_doc
toc: false
---

Core-Lib is useful when a backend has to outlive its frameworks, change its infrastructure, and stay readable while several engineers work on it. The advantages below come from one habit: business logic lives in `Service` classes, and web frameworks, databases and external APIs are created in your `CoreLib` class and used only by route handlers, `DataAccess` and `Client` classes.

> **Where it fits:** Overview. Read this after [What is Core-Lib?](index.html) if you want the practical reasons behind the six-layer structure. The costs are listed on that page under [The cost](index.html#the-cost).

## Decoupled business logic

Your services don't depend directly on Flask, SQLAlchemy, or external services. The web layer calls into your `CoreLib`; your `CoreLib` doesn't know the web layer exists.

When your framework changes, you replace the route functions. Your services, data access, and most tests stay the same. The home page shows [the same `HelloApp` behind Flask and FastAPI](index.html#calling-it-from-flask-or-fastapi).

---

## Change infrastructure without rewriting your app

A database, HTTP client or payment provider sits behind one adapter: a `DataAccess` class for data sources, a `Client` class for external APIs, and `CoreLib.__init__` for the wiring.

- Same library, different backend (Postgres → MySQL, Memcached → Redis): a config change, when the class or URL comes from YAML.
- Different library or API (SQLAlchemy → MongoDB, one payment provider → another): you rewrite that adapter. Your `Service` code does not change as long as the adapter keeps the same methods and returns the same shapes.

For a worked example, see [adding an enterprise tier](index.html#a-real-scenario-adding-an-enterprise-tier): the same code deployed twice, each process booted with its own YAML file.

---

## Run the same logic everywhere

The same `CoreLib` class runs behind web APIs, background jobs, scripts, and tests. Each process creates one instance at startup; tests create their own with a test config.

```python
# in a Flask or FastAPI route
hello_app.user.greet(user_id)

# in a Job: load_jobs() passes the object you map it to (usually your CoreLib) to initialized()
self.hello_app.user.greet(user_id)

# in a test
self.hello_app.user.greet(jane[User.id.key])
```

---

## Fast, reliable tests

Tests build the full application from a test config: SQLite instead of Postgres, fake clients instead of real services. If your queries also run on SQLite, that means no Docker and no external services.

```python
# tests/test_user.py
import unittest

from core_lib.helpers.test import load_core_lib_config

from hello_core_lib import HelloApp, User


class TestUserService(unittest.TestCase):
    def setUp(self):
        config = load_core_lib_config('./config', 'test_config.yaml')  # tests/config/, relative to this file
        self.hello_app = HelloApp(config)   # full app, test database, fake clients

    def test_greet(self):
        jane = self.hello_app.user.create('Jane')
        self.assertEqual(self.hello_app.user.greet(jane[User.id.key]), 'Hello, Jane!')
```

`HelloApp` and `User` come from the [one-file example](index.html#a-complete-core-lib-app-in-one-file). See [Testing Core-Lib](test_core_lib.html) for the config files and for sharing one instance across test files.

---

## Consistent structure across teams

Core-Lib gives every project the same six names:

- `CoreLib` — single entry point, wires everything below it
- `Service` — business logic and orchestration
- `DataAccess` — database queries
- `Client` — external APIs and third-party services
- `Job` — scheduled or background tasks
- `Connection` — session lifecycle for any data source

In a project that follows them, every engineer knows where everything lives. Projects created with `core_lib generate` start with the `CoreLib` class and the `DataAccess` and `Service` modules already in place.

---

## Keep architecture from drifting

Most systems become tightly coupled over time, not by design but through shortcuts: one imported session here, one `request` object there.

Core-Lib makes the boundary the easy path: connections and clients are built once, in your `CoreLib` class, and handed to services, so importing a session into a service is the extra work. It does not police the boundary. If you want it checked, add an import rule to CI, for example an [import-linter](https://import-linter.readthedocs.io/){:target="_blank"} `forbidden` contract that fails when your `service` package imports `flask`, `django` or `sqlalchemy`.

---

## Long-lived code

A team built a complete production system on Play Framework 1.2, with controllers, models and business logic all written to Play's API. Then Play 2.0 came out with a different architecture. Moving to it cost about as much as rebuilding the product, and the project was dropped. The framework didn't fail them; the coupling did. Most teams are not killed by one big rewrite, but slowed down by hundreds of small places where framework code leaked into business code.

A Python example: SQLAlchemy 2.0 made `Query.get()` legacy in favour of `Session.get()`. In a Core-Lib app, SQLAlchemy calls live in `DataAccess` classes, so that change touches those files and not your services. The honest trade-off: Core-Lib's own `CRUDDataAccess` still calls `Query.get()` today (run with `python -W default` to see the `LegacyAPIWarning`), so for that part you wait for a Core-Lib release.

---

## Composing Core-Libs

Each Core-Lib that `core_lib generate` creates ships a Hydra search-path plugin. Once it is installed as a package, another project can list its YAML under `defaults:`, the same way `- core_lib` works, and build it from `_target_` (see [Instantiate Config](instantiate_config.html) and [The CoreLib Class](core_lib_main_class.html)).

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="index.html">Previous</a></button>
    <button class="pageNext-btn"><a href="project_structure.html">Next</a></button>
</div>
