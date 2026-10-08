---
id: core_lib_main_class
title: The CoreLib Class
sidebar: core_lib_doc_sidebar
permalink: core_lib_main_class.html
folder: core_lib_doc
toc: false
---

`CoreLib` is the class your application is built around. You subclass it once. Its `__init__` builds your connections, data access classes and services. Then every entry point, whether a web route, a background job, a script or a test, calls that same object.

> **Where it fits:** CoreLib layer. This is the single object your web routes, jobs, scripts, and tests call; it wires everything below it.

*core_lib.core_lib.CoreLib* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/core_lib.py#L19){:target="_blank"}

This page picks up where the [one-file example](index.html#a-complete-core-lib-app-in-one-file) on the home page stops, and walks through a small real app:

1. Write the `CoreLib` subclass.
2. Move its config into a YAML file.
3. Create it once per process and call `start_core_lib()`.
4. Load the config and call the object from a script, from Flask and from Django.

After that: what you get from subclassing `CoreLib`, the rules, and how to compose several Core-Libs.

The files used on this page (paths are relative to your project folder; [Project Structure](project_structure.html) shows the full layout):

```text
your_core_lib/                  # the package
├── config/your_core_lib.yaml   # step 2
├── data_layers/                # User entity, UserDataAccess, UserService
└── your_core_lib.py            # step 1: YourCoreLib
your_core_lib_instance.py       # step 3: holds the one YourCoreLib of this process
main.py                         # step 4: a script
web.py                          # step 4: a Flask app
```

---

## 1. Write the `CoreLib` subclass

```python
# your_core_lib/your_core_lib.py
from omegaconf import DictConfig

from core_lib.core_lib import CoreLib
from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory

from your_core_lib.data_layers.data_access.user_data_access import UserDataAccess
from your_core_lib.data_layers.service.user_service import UserService


class YourCoreLib(CoreLib):
    def __init__(self, config: DictConfig):
        super().__init__()
        self.config = config

        # Connections and clients are built here, once, from config.
        db = SqlAlchemyConnectionFactory(config.core_lib.your_core_lib.data.db)

        # The DataAccess gets the connection; the Service gets the DataAccess.
        user_da = UserDataAccess(db)
        self.user = UserService(user_da)
```

A route, job, script or test then calls `your_core_lib.user.get(user_id)`. It never sees the database session.

These are the three classes it wires, one file each. They do the same job as the classes in the home page example:

```python
# your_core_lib/data_layers/data/db/entities/user.py
from sqlalchemy import Column, Integer, VARCHAR

from core_lib.data_layers.data.db.sqlalchemy.base import Base


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(255), nullable=False)
```

```python
# your_core_lib/data_layers/data_access/user_data_access.py
from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.data_layers.data_access.db.crud.crud_data_access import CRUDDataAccess

from your_core_lib.data_layers.data.db.entities.user import User


class UserDataAccess(CRUDDataAccess):
    def __init__(self, db: SqlAlchemyConnectionFactory):
        super().__init__(User, db)
```

```python
# your_core_lib/data_layers/service/user_service.py
from core_lib.data_layers.service.service import Service
from core_lib.data_transform.result_to_dict import ResultToDict

from your_core_lib.data_layers.data.db.entities.user import User
from your_core_lib.data_layers.data_access.user_data_access import UserDataAccess


class UserService(Service):
    def __init__(self, user_da: UserDataAccess):
        self._user_da = user_da

    @ResultToDict()  # callers get plain dicts, not ORM objects
    def create(self, name: str):
        return self._user_da.create({User.name.key: name})

    @ResultToDict()
    def get(self, user_id: int):
        return self._user_da.get(user_id)  # raises a 404 StatusCodeException if there is no such user
```

---

## 2. Move the config into YAML

`config.core_lib.your_core_lib.data.db` in `__init__` reads this block:

```yaml
# your_core_lib/config/your_core_lib.yaml
core_lib:
  your_core_lib:
    data:
      db:
        log_queries: false
        create_db: true        # create missing tables at startup
        url:
          protocol: sqlite
          file: your_app.db    # an SQLite file in the working directory
```

Use an SQLite file, not in-memory SQLite, once a web server is involved. With in-memory SQLite each server thread gets its own empty database, and requests fail with `no such table`.

For Postgres, set `protocol: postgresql` and fill in `username`, `password`, `host`, `port` and `file` (the database name). `${oc.env:POSTGRES_PASSWORD}` reads a value from an environment variable. See [SQLAlchemy Connection Factory](sql_alchemy_connection.html) for every key.

The YAML is loaded with [Hydra](https://hydra.cc/){:target="_blank"}, which `pip install core-lib` installs. Hydra turns the file into a `DictConfig`, the object `__init__` receives. Step 4 shows the two ways to load it.

---

## 3. Create it once per process

Build the object once, when the process starts, and have every route and job use that same object. Do not build it per request. The holder below does that. `core_lib generate` writes this file for you as `your_core_lib_instance.py` (see [Generation](generation.html)). The `start_core_lib()` line is the one addition here; the generated file leaves it out.

```python
# your_core_lib_instance.py
from your_core_lib.your_core_lib import YourCoreLib


class YourCoreLibInstance(object):
    _app_instance = None

    @staticmethod
    def init(core_lib_cfg):
        if not YourCoreLibInstance._app_instance:
            YourCoreLibInstance._app_instance = YourCoreLib(core_lib_cfg)
            YourCoreLibInstance._app_instance.start_core_lib()

    @staticmethod
    def get() -> YourCoreLib:
        return YourCoreLibInstance._app_instance
```

Your entry point calls `YourCoreLibInstance.init(config)` once at startup. Everything else calls `YourCoreLibInstance.get()`. Calling `init()` again does nothing.

### `start_core_lib()`

*core_lib.core_lib.CoreLib.start_core_lib()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/core_lib.py#L78){:target="_blank"}

Call it once, after the object is built. It tells listeners the app is ready: every attached [`CoreLibListener`](core_lib_listener.html) gets `on_core_lib_ready()`. Calling it a second time on the same object raises `CoreLibInitException`.

It does not start your jobs. Jobs are scheduled earlier, when your `__init__` calls `load_jobs()` (see [Job](job.html)). A job that is also a `CoreLibListener` gets `on_core_lib_ready()` here, like any other listener. If nothing is listening, `start_core_lib()` only logs a line. Call it anyway, so adding a listener later does not mean changing your startup code.

### Why only one per process

A few parts of Core-Lib are class attributes of `CoreLib`, so they exist once per Python process, not once per object: `cache_registry`, `observer_registry`, `connection_factory_registry`, `handle_exception_middleware` and the job `scheduler`. A second `YourCoreLib(...)` in the same process shares all of them with the first one.

So if your `__init__` registers a cache handler under a fixed name, building the class a second time fails:

```text
ValueError: cache by key "your_core_lib" already registerd for type "<class 'core_lib.cache.cache_handler_ram.CacheHandlerRam'>"
```

Guard every registration, so a second construction (in tests, for example) is safe:

```python
from core_lib.cache.cache_handler_ram import CacheHandlerRam
from core_lib.core_lib import CoreLib

YOUR_CORE_LIB_CACHE = 'your_core_lib'

# inside YourCoreLib.__init__
if not CoreLib.cache_registry.get(YOUR_CORE_LIB_CACHE):
    CoreLib.cache_registry.register(YOUR_CORE_LIB_CACHE, CacheHandlerRam())
```

Even when nothing fails, a second instance builds its connections again while sharing the cache, the observers and the scheduler with the first. Two configs in one process do not give you two separate apps. If you need two setups, for example a consumer tier and an enterprise tier, deploy the same code twice and start each process with its own config.

Web servers such as gunicorn or uWSGI run several worker processes. Each worker builds its own `CoreLib` once. That is expected.

---

## 4. Load the config and call it

### A script or worker: `@hydra.main`

```python
# main.py
import hydra
from omegaconf import DictConfig

from your_core_lib_instance import YourCoreLibInstance


@hydra.main(config_path='your_core_lib/config', config_name='your_core_lib', version_base=None)
def main(config: DictConfig):
    YourCoreLibInstance.init(config)  # once, at startup

    print(YourCoreLibInstance.get().user.create('Jane'))


if __name__ == '__main__':
    main()
```

`python main.py` prints `{'id': 1, 'name': 'Jane'}` on the first run. The id grows on each run, because the SQLite file keeps its rows.

`@hydra.main` reads the YAML, applies command-line overrides and passes the result to `main()`. For example, `python main.py core_lib.your_core_lib.data.db.url.file=other.db` uses a different database file. Hydra also writes a log and a copy of the config for each run under `outputs/<date>/<time>/`. That is Hydra's default behaviour, not something Core-Lib adds.

### Flask

`@hydra.main` expects to own the program's entry point. A web server imports your module instead, so load the YAML with Hydra's compose API when the module is imported:

```python
# web.py
from flask import Flask, request
from hydra import compose, initialize

from core_lib.web_helpers.decorators import HandleException
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils

from your_core_lib_instance import YourCoreLibInstance

# Runs once per process, when the server imports this module.
with initialize(config_path='your_core_lib/config', version_base=None):
    YourCoreLibInstance.init(compose(config_name='your_core_lib'))
WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)

app = Flask(__name__)


@app.post('/users')
@HandleException()
def create_user():
    return YourCoreLibInstance.get().user.create(request.json['name']), 201


@app.get('/users/<int:user_id>')
@HandleException()
def get_user(user_id):
    return YourCoreLibInstance.get().user.get(user_id)
```

Run it with `flask --app web run`. Against a fresh database:

```text
POST /users  {"name": "Jane"}   ->  201  {"id": 1, "name": "Jane"}
GET  /users/1                   ->  200  {"id": 1, "name": "Jane"}
GET  /users/42                  ->  404  {"message": "Not Found"}
```

The routes only read the request, call the service and return the result. `config_path` is relative to the file that calls `initialize()`.

`@HandleException()` and `WebHelpersUtils.init()` are optional [Web Helpers](web.html). `UserDataAccess.get()` raises a 404 `StatusCodeException` for a missing user, and `@HandleException()` turns it into the 404 response above instead of a 500 ([Handle Exceptions](handle_exceptions.html)). `WebHelpersUtils.init()` tells the helpers to build Flask responses. For login checks, see [User Security](user_security.html).

### Django

Django's place for startup code is `AppConfig.ready()`:

```python
# users/apps.py
from django.apps import AppConfig
from hydra import compose, initialize

from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils

from your_core_lib_instance import YourCoreLibInstance


class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):  # Django calls this at startup, in each process
        with initialize(config_path='../your_core_lib/config', version_base=None):
            YourCoreLibInstance.init(compose(config_name='your_core_lib'))
        WebHelpersUtils.init(WebHelpersUtils.ServerType.DJANGO)
```

```python
# users/views.py
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from core_lib.web_helpers.decorators import HandleException

from your_core_lib_instance import YourCoreLibInstance


@require_GET
@HandleException()
def get_user(request, user_id):
    return JsonResponse(YourCoreLibInstance.get().user.get(user_id))
```

Add `'users.apps.UsersConfig'` to `INSTALLED_APPS` and route `path('users/<int:user_id>', views.get_user)`. As in Flask, `GET /users/1` returns the user and `GET /users/42` returns a 404.

With the auto-reloader on, `manage.py runserver` runs `ready()` in two processes: the file watcher and the server. So in development you will see two startups, one in each process. If that matters, for example because your `__init__` schedules jobs, use `runserver --noreload`.

### Tests

Tests build the same class from a test config, usually SQLite plus mock clients. See [Testing Core-Lib](test_core_lib.html) for `load_core_lib_config()` and for sharing one instance across test files.

---

## What you get from subclassing `CoreLib`

| Member | What it does |
|---|---|
| `super().__init__()` | Sets up the listener list and the "started" flag. Call it first in your `__init__`. |
| `start_core_lib()` | Fires `on_core_lib_ready()` on attached listeners. Raises `CoreLibInitException` if called twice. |
| `attach_listener()` / `detach_listener()` | Subscribe or unsubscribe a [`CoreLibListener`](core_lib_listener.html). |
| `fire_core_lib_destroy()` | Fires `on_core_lib_destroy()`. Called from `__del__` when the object is garbage-collected. |
| `load_jobs(config, job_to_data_handler)` | Builds the jobs declared in YAML and schedules them on `CoreLib.scheduler`. See [Job](job.html). |
| `CoreLib.cache_registry`, `CoreLib.observer_registry`, `CoreLib.connection_factory_registry` | Process-wide registries. `@Cache` looks up its cache handler here, `@Observe` its observer, and `get_or_reg()` shares connection factories. See [Registry](registry.html). |
| `CoreLib.handle_exception_middleware` | The middleware chain that `@HandleException` runs when a route fails. See [Middleware](middleware.html). |
| `CoreLib.scheduler` | The `JobScheduler` that `load_jobs()` uses. |

If you use none of these, `CoreLib` is simply the base class that marks where your app is wired, and that is fine.

---

## Rules

1. **Build all infrastructure in `__init__`.** Connections, clients, caches: nowhere else. Service code never imports a session, a Redis client, or an SDK. Core-Lib does not check this for you; it is the convention that keeps services free of framework and database code.
2. **Always call `super().__init__()` first.** It sets up the listener list and the "started" flag that `attach_listener()` and `start_core_lib()` use.
3. **Services receive their collaborators (DataAccess, Clients, other services) as constructor arguments.** The exception is a few cross-cutting pieces that use process-wide state. `@Cache`, `@Observe` and `@HandleException` look up objects on the `CoreLib` class, `@RequireLogin` uses the `SecurityHandler` singleton, and the web helpers read `WebHelpersUtils.server_type`. Set these up once per process, at startup.
4. **One app per process.** Build your `CoreLib` once per process (step 3). Different setups are different deployments, each with its own config.

That is what keeps services independent from frameworks, keeps code testable without external services, and keeps the structure from drifting over time.

---

## `__init__()`

*core_lib.core_lib.CoreLib.\_\_init\_\_()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/core_lib.py#L26){:target="_blank"}

`CoreLib.__init__()` takes no arguments. Your subclass takes the config and calls it first:

```python
class YourCoreLib(CoreLib):
    def __init__(self, config: DictConfig):
        super().__init__()
        ...
```

---

## Composing multiple `CoreLib`s

For larger systems you can build one Core-Lib inside another. This is useful when a sub-system, such as an email module, is itself a self-contained Core-Lib that you want to drop in. Build it in your `__init__`, directly or from YAML via Hydra's `_target_`. See [Instantiate Config](instantiate_config.html) for the pattern.

A composed Core-Lib is built once, inside your top-level one, so the process still runs one app. All Core-Libs in a process share the registries and the scheduler on the `CoreLib` class, so:

- Register each cache handler under its own name, pass that name to `@Cache(handler_name=...)`, and guard every registration as shown in step 3.
- To have them share one database pool instead of opening one each, build the connection with `CoreLib.connection_factory_registry.get_or_reg(config)` (see [Registry](registry.html)).

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="glossary.html">Previous</a></button>
    <button class="pageNext-btn"><a href="registry.html">Next</a></button>
</div>
