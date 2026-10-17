[![PyPI](https://img.shields.io/pypi/v/core-lib)](https://pypi.org/project/core-lib/)
![PyPI - License](https://img.shields.io/pypi/l/core-lib)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/core-lib)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/core-lib.svg)](https://pypistats.org/packages/core-lib)
[![GitHub stars](https://img.shields.io/github/stars/shay-te/core-lib?style=social)](https://github.com/shay-te/core-lib)

# Core-Lib

**Core-Lib is a Python library for structuring backends.** You wire your services, data access and API clients once, in one `CoreLib` class. Your web routes, background jobs, scripts and tests all call that same object.

**It is not a web framework and not an ORM.** You keep Flask, Django or FastAPI, and you keep SQLAlchemy. Core-Lib gives that code a fixed place to live, so framework and database code stays at the edges and replacing one of them touches the edges, not your business logic.

```text
Web / Jobs / Tests  →  CoreLib  →  Service  →  DataAccess  →  Database
                                      │
                                      └──→  Client  →  External API
```

It is not a DI container either: you wire objects by hand in `__init__`. What the package adds is the plumbing around that wiring (see [What the package ships](#what-the-package-ships)).

---

## Quickstart

```bash
pip install core-lib        # Python 3.10+
```

```python
# hello_core_lib.py — one file, copy and run
from omegaconf import OmegaConf
from sqlalchemy import Column, Integer, VARCHAR

from core_lib.core_lib import CoreLib
from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.data_layers.data.db.sqlalchemy.base import Base
from core_lib.data_layers.data_access.db.crud.crud_data_access import CRUDDataAccess
from core_lib.data_layers.service.service import Service
from core_lib.data_transform.result_to_dict import ResultToDict


class User(Base):                                # Entity: a SQLAlchemy model
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(255), nullable=False)


class UserDataAccess(CRUDDataAccess):            # DataAccess: create/get/update/delete
    def __init__(self, db):
        super().__init__(User, db)


class UserService(Service):                      # Service: business logic
    def __init__(self, user_data_access: UserDataAccess):
        self._user_data_access = user_data_access

    @ResultToDict()                              # callers get a plain dict
    def create(self, name: str) -> dict:
        return self._user_data_access.create({User.name.key: name})

    def greet(self, user_id: int) -> str:
        return f'Hello, {self._user_data_access.get(user_id).name}!'


class HelloApp(CoreLib):                         # CoreLib: wires it all, once
    def __init__(self, config):
        super().__init__()
        db = SqlAlchemyConnectionFactory(config.db)
        self.user = UserService(UserDataAccess(db))


config = OmegaConf.create({'db': {'create_db': True, 'url': {'protocol': 'sqlite'}}})

if __name__ == '__main__':
    hello_app = HelloApp(config)
    jane = hello_app.user.create('Jane')
    print(hello_app.user.greet(jane[User.id.key]))   # Hello, Jane!
```

Run `python hello_core_lib.py`. It prints `Hello, Jane!`, using an in-memory SQLite database: no server, no Docker, no config files. The `if __name__ == '__main__':` guard lets a web app or a test import `HelloApp` without running the demo.

What Core-Lib did for you here: `CRUDDataAccess` gave `UserDataAccess` its `create`, `get`, `update` and `delete`; `SqlAlchemyConnectionFactory` created the tables and opened, committed and closed a session for every call; `@ResultToDict()` turned the new row into a plain dict.

---

## The same object behind Flask or FastAPI

```python
# web.py
from fastapi import FastAPI
from flask import Flask
from omegaconf import OmegaConf

from hello_core_lib import HelloApp

# A SQLite file instead of in-memory: web servers answer requests on worker threads,
# and an in-memory SQLite database only exists in the thread that created it.
config = OmegaConf.create({'db': {'create_db': True, 'url': {'protocol': 'sqlite', 'file': 'hello.db'}}})
hello_app = HelloApp(config)    # once per process, at startup, never per request

# Flask
flask_app = Flask(__name__)

@flask_app.get('/users/<int:user_id>/greeting')
def flask_greet(user_id):
    return {'message': hello_app.user.greet(user_id)}

# FastAPI: HelloApp and UserService are the same objects, untouched
fastapi_app = FastAPI()

@fastapi_app.get('/users/{user_id}/greeting')
def fastapi_greet(user_id: int):
    return {'message': hello_app.user.greet(user_id)}
```

Moving from Flask to FastAPI means rewriting the route functions, and nothing behind `hello_app`. Core-Lib's optional web helpers (`response_json`, `@RequireLogin`, `@HandleException`) support Flask and Django only; with FastAPI you call the `CoreLib` object from your routes directly.

---

## What the package ships

`Service` and `DataAccess` are empty base classes; the structure is a convention, not something the library checks. The code you get is the plumbing around it:

- **Connections:** factories for SQLAlchemy, MongoDB, Solr, Neo4j and Elasticsearch that manage the session lifecycle (`with db.get() as session:`).
- **Data access:** `CRUDDataAccess`, plus soft-delete variants, and `RuleValidator` for the fields a caller may write.
- **Services:** `@Cache` (RAM, Memcached and Redis handlers), `@ResultToDict()`, `@NotFoundErrorHandler()`, `@DuplicateErrorHandler()`, `StatusCodeException`, observer events.
- **Wiring:** `instantiate_config`, which builds the class named by `_target_` in YAML (Hydra).
- **Jobs:** background and scheduled jobs declared in YAML.
- **Web:** Flask and Django helpers for JSON responses, login checks, error handling and JWT sessions.
- **Tests:** `load_core_lib_config`, which loads a test YAML that swaps Postgres for SQLite and real clients for fakes.
- **Tooling:** the `core_lib` command for Alembic migrations (`core_lib migrate`) and project scaffolding (`core_lib generate`).

## Why not just use SQLAlchemy and Flask directly?

You can, and for a script or a small app you should. Core-Lib does not replace them: inside a `DataAccess` you write normal SQLAlchemy, and your routes are normal Flask, Django or FastAPI routes. The problem shows up as the code grows: services read Flask's `request`, business logic opens its own sessions, and tests need a real database and real APIs. Core-Lib gives that code a fixed place, and builds the connections and clients once, in your `CoreLib` class, from config.

## Why not just do this with discipline?

You can do that too: the pattern is plain constructor injection, and Core-Lib does not stop a service from importing `flask.request`. What it saves you is writing and maintaining the plumbing listed above. If you need none of it, plain constructor injection is enough. The docs show [the same app with and without Core-Lib](https://shay-te.github.io/core-lib/index.html#why-not-just-do-this-with-discipline-without-the-library), and a worked example of [adding an enterprise tier](https://shay-te.github.io/core-lib/advantages.html#adding-an-enterprise-tier) by deploying the same code with a different YAML file.

## The cost

- `pip install core-lib` installs everything in `requirements.txt`: Hydra, SQLAlchemy and Alembic, drivers for PostgreSQL, MySQL, MongoDB, Solr, Neo4j, Redis and Memcached, boto3, GeoAlchemy2 and Shapely, **both Flask and Django**, and some test libraries (moto, freezegun, mongomock, python-dotenv). The Elasticsearch client is not included.
- SQLAlchemy (2.0.52) and Hydra (1.3.6) are pinned to exact versions, so you upgrade them when Core-Lib does.
- Core-Lib is pre-1.0 (0.2.x), and is designed for one `CoreLib` wiring per process: its cache, observer and connection registries are class-level.

---

## When to use it

Use it when:
- Your backend will live for years, not weeks
- Multiple engineers will touch the same codebase
- You want to run the same logic from web, jobs, scripts, and tests
- You want to change infrastructure (DB, cache, HTTP client) without touching business logic

Don't use it when:
- Your app is a prototype, script, or simple CRUD app
- Your app is small and unlikely to change much

---

## Documentation

Full documentation, examples, and guides: [https://shay-te.github.io/core-lib/](https://shay-te.github.io/core-lib/)

---

## Running tests

```bash
python -m unittest discover -v
```

## License

Core-Lib is licensed under [MIT](https://github.com/shay-te/core-lib/blob/master/LICENSE)
