---
id: glossary
title: Glossary
sidebar: core_lib_doc_sidebar
permalink: glossary.html
folder: core_lib_doc
toc: false
---

A short reference for terms used throughout these docs. Familiarity with most of these is assumed; this page is a quick lookup, not a tutorial.

## Core-Lib terms

**`CoreLib`** — The base class your application inherits from. Your subclass builds connections, data access and services in its `__init__`. Create it once per process, at startup; web routes, jobs, scripts and tests all call that one object. See [The CoreLib Class](core_lib_main_class.html).

**`Service`** — A class that owns business logic for one area of the app (users, orders, subscriptions). Calls `DataAccess` and `Client`; never opens a database session or HTTP client directly. See [Data Layers](data_layers.html).

**`DataAccess`** — A class that wraps one ORM entity (or one collection / index / data source) and exposes the queries the rest of the app needs. Talks to a `Connection`; never holds business rules. See [Data Layers](data_layers.html) and [CRUD Data Access](crud.html).

**`Client`** — A class that wraps one external HTTP API. Subclasses `ClientBase`. See [Client Base](client_base.html).

**`Job`** — A background or scheduled task, declared in YAML. `CoreLib.load_jobs()` builds each job from its config (constructor arguments come from the YAML) and schedules it. Map the job's name to a handler, usually your `CoreLib`, and the job receives it in `initialized(data_handler)`. The scheduler then calls `run()`, which calls the handler's services. See [Job](job.html).

**`Connection`** — A context manager (`with conn.get() as session:`) that handles the open / commit / close lifecycle for a data source. Each backend has its own factory class. See [Connection](connection.html).

**Entity** — A Python class that maps to one database table (an SQLAlchemy ORM model). Lives in `data_layers/data/db/entities/` (see [Project Structure](project_structure.html)). The `DataAccess` for an entity wraps queries against it.

**Edge** — The code that touches the outside world: route handlers, job entry points, your `CoreLib.__init__` (where connections and clients are built), and the `DataAccess` and `Client` classes that use them. Services sit behind the edge and only call those classes, so replacing a framework or a database changes edge code, not services.

## Python / web terms used in the docs

**ORM** — Object-Relational Mapper. A library that maps database rows to Python objects so you write Python instead of SQL. SQLAlchemy is the one Core-Lib uses by default.

**Session** — The SQLAlchemy object you use to run queries inside a transaction. `with db.get() as session: session.get(User, 1)`. Each `with` block opens, commits, and closes one session automatically.

**Session (login)** — On the [User Security](user_security.html) page, "session" means the logged-in user's data, decoded from the auth token (for example, from a cookie). It is not a database session.

**Context manager** — A Python object you use in a `with` block. Its `__enter__` runs at the start, its `__exit__` at the end (even on exception). All Core-Lib `Connection` classes are context managers — that's what `with conn.get() as session:` is.

**Decorator** — A function that wraps another function to change its behavior. Written as `@Decorator` above a `def`. Core-Lib uses decorators for `@Cache`, `@ResultToDict`, `@Observe`, `@RequireLogin`, `@HandleException`, and more.

**WSGI** — Python's standard interface between a web server (Gunicorn, uWSGI) and a web framework (Flask, Django). `UserAuthMiddleware` for Flask plugs into the WSGI layer; for Django it plugs into the framework's middleware list.

**Hydra / OmegaConf** — The config libraries Core-Lib uses. `OmegaConf` is the dict-like config object (`DictConfig`). `Hydra` loads YAML files (`@hydra.main` or `compose()`), adds composition (load one YAML, layer another on top) and `_target_` instantiation (a YAML key that says "build an instance of this class"). See [The CoreLib Class](core_lib_main_class.html#2-move-the-config-into-yaml) for loading config and [Instantiate Config](instantiate_config.html) for `_target_`.

**Mixin** — A small class designed to be combined with other classes via multiple inheritance. `SoftDeleteMixin` is a mixin: you inherit from both `Base` and `SoftDeleteMixin` and the entity gets the mixin's columns. See [Soft Delete Handler](soft_delete.html).

**Fixture** — In testing, a pre-built object or state your tests use. Core-Lib aims for *no* fixtures: you boot the full app against SQLite with one config override and call the real `Service` methods.

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="project_structure.html">Previous</a></button>
    <button class="pageNext-btn"><a href="core_lib_main_class.html">Next</a></button>
</div>
