---
id: test_core_lib
title: Testing Core-Lib
sidebar: core_lib_doc_sidebar
permalink: test_core_lib.html
folder: core_lib_doc
toc: false
---

Tests should build the same `CoreLib` class your app uses in production, with test wiring: in-memory SQLite instead of Postgres, and a mock instead of a real HTTP client. The services, data access classes and decorators under test stay the real ones.

What Core-Lib adds here is small. `load_core_lib_config()` is a short helper that clears the process-wide cache and observer registries and Hydra's global state, then loads your test config. The rest of this page is a pattern: one override file that swaps the database and the clients, shown on a small project you can copy and run.

> **Where it fits:** Testing harness. Tests construct your `CoreLib` from a test config and call its Services directly — the same way a web route or job would in production.

## load_core_lib_config()

*core_lib.helpers.test.load_core_lib_config()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/test.py){:target="_blank"}

Every test that creates a `CoreLib` instance needs a clean slate: no cache handlers or observers left registered by an earlier test, and a freshly initialized Hydra. `load_core_lib_config()` does both in one call.

```python
def load_core_lib_config(path: str, config_file: str = 'config.yaml', caller_stack_depth: int = 2):
```

**Arguments**

- **`path`** *`(str)`*: Path to the config directory, **relative to the file that calls `load_core_lib_config()`**, not to the working directory. From `tests/test_user.py`, `'./config'` means `tests/config/`.
- **`config_file`** *`(str)`*: Default `'config.yaml'`. Name of the config file to load.
- **`caller_stack_depth`** *`(int)`*: Default `2`. Passed to `hydra.initialize` to find the calling file. Leave it as is.

**Returns**

*`(DictConfig)`*: The composed Hydra config, ready to pass to your `CoreLib` constructor.

**Example**

```python
# tests/test_user.py
from core_lib.helpers.test import load_core_lib_config

config = load_core_lib_config('./config', 'test_config.yaml')  # loads tests/config/test_config.yaml
user_core_lib = UserCoreLib(config)
```

What it does:
1. Unregisters every key from `CoreLib.cache_registry` and `CoreLib.observer_registry`
2. Clears Hydra's global state
3. Initializes Hydra with the given config path
4. Returns the composed config

It does not reset `CoreLib.connection_factory_registry` or `CoreLib.scheduler`. Hydra prints a `version_base` warning when it loads the config; it is harmless.

---

## The example project

The rest of the page builds this project. Every folder except `tests/config/` holds an empty `__init__.py`, so `user_core_lib` and `tests` import as packages. Run the tests from `user_project/`.

```text
user_project/
├── user_core_lib/
│   ├── user_core_lib.py               # UserCoreLib: the wiring
│   ├── client/
│   │   └── user_client.py             # UserClient: HTTP calls to a remote user directory
│   ├── config/
│   │   └── user_core_lib.yaml         # production config
│   └── data_layers/
│       ├── data/db/entities/user.py   # User
│       ├── data_access/user_data_access.py
│       └── service/user_service.py
└── tests/
    ├── config/
    │   ├── test_config.yaml           # what the tests load
    │   └── test_config_override.yaml  # what the tests change
    ├── user_client_mock.py            # UserClientMock: replaces UserClient
    └── test_user.py
```

## The app

### Entity and DataAccess

`DataAccess` wraps database queries. Tests keep the real one; only the database behind it changes.

```python
# user_core_lib/data_layers/data/db/entities/user.py
from sqlalchemy import Column, INTEGER, VARCHAR

from core_lib.data_layers.data.db.sqlalchemy.base import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(length=255), nullable=False)
    contact = Column(VARCHAR(length=255), nullable=False)
```

```python
# user_core_lib/data_layers/data_access/user_data_access.py
from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.data_layers.data_access.db.crud.crud_data_access import CRUDDataAccess

from user_core_lib.data_layers.data.db.entities.user import User


class UserDataAccess(CRUDDataAccess):
    def __init__(self, db: SqlAlchemyConnectionFactory):
        super().__init__(User, db)
```

### Client

The client calls a remote user directory over HTTP. In tests it is replaced by a mock.

```python
# user_core_lib/client/user_client.py
from core_lib.client.client_base import ClientBase


class UserClient(ClientBase):
    """Talks to a remote user directory over HTTP. Returns plain dicts, not Response objects."""

    def get(self, user_id: int) -> dict:
        return self._get(f'/user/{user_id}').json()

    def create(self, data: dict) -> dict:
        return self._post('/user', json=data).json()
```

### Service

`UserService` is the business API your tests call. It receives the DataAccess and the client from `UserCoreLib.__init__`, the same way in production and in tests. `import_user()` uses both.

```python
# user_core_lib/data_layers/service/user_service.py
from core_lib.data_layers.service.service import Service
from core_lib.data_transform.result_to_dict import ResultToDict

from user_core_lib.client.user_client import UserClient
from user_core_lib.data_layers.data.db.entities.user import User
from user_core_lib.data_layers.data_access.user_data_access import UserDataAccess


class UserService(Service):
    def __init__(self, user_da: UserDataAccess, user_client: UserClient):
        self._user_da = user_da
        self._user_client = user_client

    @ResultToDict()
    def create(self, name: str, contact: str):
        return self._user_da.create({User.name.key: name, User.contact.key: contact})

    @ResultToDict()
    def get(self, user_id: int):
        return self._user_da.get(user_id)  # raises a 404 StatusCodeException if there is no such user

    def update(self, user_id: int, data: dict):
        self._user_da.update(user_id, data)

    def delete(self, user_id: int):
        self._user_da.delete(user_id)

    @ResultToDict()
    def import_user(self, remote_user_id: int):
        """Copy a user from the remote user directory into our database."""
        remote_user = self._user_client.get(remote_user_id)
        return self._user_da.create({User.name.key: remote_user['name'], User.contact.key: remote_user['contact']})
```

### Config and the `CoreLib` class

This is the production config. The database is Postgres, with its connection details read from environment variables, and the client is the real `UserClient`.

```yaml
# user_core_lib/config/user_core_lib.yaml
core_lib:
  user_core_lib:
    data:
      db:
        log_queries: false
        create_db: false              # production tables come from migrations
        url:
          protocol: postgresql
          username: ${oc.env:USERDB_USER}
          password: ${oc.env:USERDB_PASSWORD}
          host: ${oc.env:USERDB_HOST}
          port: ${oc.env:USERDB_PORT}
          file: ${oc.env:USERDB_DB}   # the database name
    client:
      user_client:
        _target_: user_core_lib.client.user_client.UserClient
        base_url: https://users.example.com/
```

`UserCoreLib` builds the connection, the client and the service once, and exposes the service as `user`:

```python
# user_core_lib/user_core_lib.py
from omegaconf import DictConfig

from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.core_lib import CoreLib
from core_lib.helpers.config_instances import instantiate_config

from user_core_lib.data_layers.data_access.user_data_access import UserDataAccess
from user_core_lib.data_layers.service.user_service import UserService


class UserCoreLib(CoreLib):
    def __init__(self, config: DictConfig):
        super().__init__()
        self.config = config
        db = SqlAlchemyConnectionFactory(config.core_lib.user_core_lib.data.db)
        user_client = instantiate_config(config.core_lib.user_core_lib.client.user_client)  # the class named in _target_
        self.user = UserService(UserDataAccess(db), user_client)
```

`instantiate_config()` builds whatever class `_target_` names, passing it the other keys (`base_url`). That is what lets the test config swap in a different class. See [Instantiate Config](instantiate_config.html).

## The test config

The test config loads the production config, then merges one override file on top. The override makes two changes: in-memory SQLite instead of Postgres, and `UserClientMock` instead of `UserClient`.

```yaml
# tests/config/test_config_override.yaml
core_lib:
  user_core_lib:
    data:
      db:
        create_db: true          # create the tables at startup
        url:
          protocol: sqlite       # in-memory SQLite instead of Postgres
          username: null         # clear the rest of the production URL (see below)
          password: null
          host: null
          port: null
          file: null
    client:
      user_client:
        _target_: tests.user_client_mock.UserClientMock   # no network
```

Hydra merges dictionaries key by key. Setting `protocol: sqlite` alone would keep `username`, `host` and the rest from the production URL: the test would fail with `Environment variable 'USERDB_DB' not found`, or, with the variables set, with `Invalid SQLite URL: sqlite://<user>:***@<host>:<port>/<database>`. So the override sets every other URL key to `null`. `base_url` is not overridden, so the mock receives the production value.

The key paths under `core_lib:` must match the production config exactly. A typo does not raise an error; it adds a new key, and the override silently does not apply.

```yaml
# tests/config/test_config.yaml
defaults:
  - user_core_lib                  # the production config
  - test_config_override           # the test changes, merged on top
  - _self_

hydra:
  searchpath:
    - pkg://user_core_lib.config   # where Hydra finds user_core_lib.yaml
```

`hydra.searchpath` adds the `user_core_lib/config/` package folder to the places Hydra looks for configs, so the production YAML is used as it is, not copied. Projects made by `core_lib generate` get a Hydra search path plugin in `hydra_plugins/` that does the same.

## The test

The mock has the same methods as `UserClient`, backed by a dictionary instead of HTTP:

```python
# tests/user_client_mock.py
from core_lib.client.client_base import ClientBase


class UserClientMock(ClientBase):
    """Replaces UserClient in tests: the same methods, backed by a dict instead of HTTP."""

    users = {}  # remote users by id; a test adds the ones it needs

    def get(self, user_id: int) -> dict:
        return UserClientMock.users[user_id]

    def create(self, data: dict) -> dict:
        user = {'id': len(UserClientMock.users) + 1, **data}
        UserClientMock.users[user['id']] = user
        return user
```

```python
# tests/test_user.py
import unittest

from core_lib.error_handling.status_code_exception import StatusCodeException
from core_lib.helpers.test import load_core_lib_config

from tests.user_client_mock import UserClientMock
from user_core_lib.data_layers.data.db.entities.user import User
from user_core_lib.user_core_lib import UserCoreLib


class TestUserCoreLib(unittest.TestCase):

    def setUp(self):
        config = load_core_lib_config('./config', 'test_config.yaml')  # tests/config, relative to this file
        self.user_core_lib = UserCoreLib(config)  # a fresh in-memory database for every test

    def test_user_round_trip(self):
        # The real UserService and UserDataAccess, on SQLite.
        john = self.user_core_lib.user.create('John', '123456')
        user_id = john[User.id.key]

        self.user_core_lib.user.update(user_id, {User.name.key: 'John Doe'})

        fetched = self.user_core_lib.user.get(user_id)
        self.assertEqual('John Doe', fetched[User.name.key])
        self.assertEqual('123456', fetched[User.contact.key])

        self.user_core_lib.user.delete(user_id)
        with self.assertRaises(StatusCodeException):
            self.user_core_lib.user.get(user_id)

    def test_import_user(self):
        # UserService calls its client. The test config swapped in UserClientMock, so no HTTP request is made.
        UserClientMock.users[7] = {'id': 7, 'name': 'Jane', 'contact': '999'}

        jane = self.user_core_lib.user.import_user(7)

        self.assertEqual('Jane', self.user_core_lib.user.get(jane[User.id.key])[User.name.key])
```

Run it from `user_project/` with `python -m unittest discover` or `pytest`. No environment variables, database server or network are needed: `test_config.yaml` loads `user_core_lib.yaml` and then `test_config_override.yaml`, so the SQLite URL and the mock win. `create_db: true` creates the tables when the connection is built, and because every test builds a new `UserCoreLib`, every test starts with an empty in-memory database.

`test_import_user` goes through the real `UserService.import_user()`: the service calls its client, gets the mock's dict, and writes a real row to SQLite.

## Testing Multiple Services with a Shared Instance

Building the `CoreLib` in every `setUp()` is simple, but it repeats the startup work (connections, table creation) for every test. To build it once per test run instead, keep one shared instance in a small helper and have every test file use it. The trade-off: every test in the run shares one database, so a test should not assume an empty table or a particular id.

```python
# tests/helpers/utils.py
import os
import threading

from dotenv import load_dotenv

from core_lib.core_lib import CoreLib
from core_lib.helpers.test import load_core_lib_config

from user_core_lib.user_core_lib import UserCoreLib


class UserCoreLibInstance(object):
    instance = None


_lock = threading.Lock()


def get_core_lib() -> UserCoreLib:
    with _lock:  # build it only once, even if two tests start at the same time
        if not UserCoreLibInstance.instance:
            # Optional: environment variables your config reads with ${oc.env:...}.
            load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
            config = load_core_lib_config('../config', 'test_config.yaml')  # tests/config, relative to this file
            UserCoreLibInstance.instance = UserCoreLib(config)
            UserCoreLibInstance.instance.start_core_lib()

        # Empty every registered cache, so a value cached by one test is not seen by the next.
        for key in CoreLib.cache_registry.registered():
            CoreLib.cache_registry.get(key).flush_all()
    return UserCoreLibInstance.instance
```

`tests/helpers/` needs an empty `__init__.py` too. The config path is relative to `utils.py`, so `'../config'` is the same `tests/config/` folder as before.

Each test file calls `get_core_lib()` in `setUp()`. The first call builds the instance; later calls reuse it and empty the caches.

```python
# tests/test_user_service.py
import unittest

from tests.helpers.utils import get_core_lib
from user_core_lib.data_layers.data.db.entities.user import User


class TestUserService(unittest.TestCase):

    def setUp(self):
        self.user_core_lib = get_core_lib()

    def test_create_and_get(self):
        jane = self.user_core_lib.user.create('Jane', '555')
        self.assertEqual('Jane', self.user_core_lib.user.get(jane[User.id.key])[User.name.key])
```

```python
# tests/test_user_import.py
import unittest

from tests.helpers.utils import get_core_lib
from tests.user_client_mock import UserClientMock
from user_core_lib.data_layers.data.db.entities.user import User


class TestUserImport(unittest.TestCase):

    def setUp(self):
        self.user_core_lib = get_core_lib()

    def test_import_user(self):
        UserClientMock.users[8] = {'id': 8, 'name': 'Bob', 'contact': '777'}
        bob = self.user_core_lib.user.import_user(8)
        self.assertEqual('Bob', bob[User.name.key])
        self.assertEqual('777', bob[User.contact.key])
```

More examples are available in the [Core-Lib repository](https://github.com/shay-te/core-lib){:target="_blank"}.

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="constants.html">Previous</a></button>
    <button class="pageNext-btn"><a href="observer.html">Next</a></button>
</div>
