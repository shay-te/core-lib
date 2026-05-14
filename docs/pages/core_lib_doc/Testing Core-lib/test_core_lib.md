---
id: test_core_lib
title: Testing Core-Lib
sidebar: core_lib_doc_sidebar
permalink: test_core_lib.html
folder: core_lib_doc
toc: false
---

Let's understand how `Core-Lib` is initialized and tested and how to integrate it with your new or existing application.

## load_core_lib_config()

*core_lib.helpers.test.load_core_lib_config()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/test.py){:target="_blank"}

Every test that creates a `CoreLib` instance needs a clean slate — no stale cache or observer registrations from a previous test, and a freshly initialized Hydra config. `load_core_lib_config()` does all of this in one call.

```python
def load_core_lib_config(path: str, config_file: str = 'config.yaml', caller_stack_depth: int = 2):
```

**Arguments**

- **`path`** *`(str)`*: Path to the config directory, relative to the calling file.
- **`config_file`** *`(str)`*: Default `'config.yaml'`. Name of the config file to load.
- **`caller_stack_depth`** *`(int)`*: Default `2`. Passed to `hydra.initialize` to resolve the config path relative to the caller's location.

**Returns**

*`(DictConfig)`*: The composed Hydra config, ready to pass to your `CoreLib` constructor.

**Example**

```python
from core_lib.helpers.test import load_core_lib_config

config = load_core_lib_config('./tests/config', 'test_config.yaml')
core_lib = YourCoreLib(config)
```

What it does internally:
1. Unregisters all keys from `CoreLib.cache_registry` and `CoreLib.observer_registry`
2. Clears the global Hydra state
3. Initializes Hydra with the given config path
4. Returns the composed config

---

## DataAccess
The `DataAccess` layer is the facade of the data layer, consisting of `API` functions that will access our data sources, such as database connections and entities.

### `user_data_access.py`

```python
from http import HTTPStatus

from core_lib.data_layers.data_access.db.crud.crud_data_access import CRUDDataAccess
from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.error_handling.status_code_exception import StatusCodeException
from user_core_lib.data_layers.data.db.user import User
from core_lib.error_handling.not_found_decorator import NotFoundErrorHandler


class UserDataAccess(CRUDDataAccess):
    def __init__(self, db: SqlAlchemyConnectionFactory):
        CRUDDataAccess.__init__(self, User, db)
```

## Service 
The `Service` layer is a facade of the `DataAccess` layer and connections. consisting of `API` functions that will handle business logic, data transformation, and caching.

### `user_service.py`

```python
from core_lib.data_transform.result_to_dict import ResultToDict
from core_lib.data_layers.service.service import Service
from user_core_lib.data_layers.data_access.user_data_access import UserDataAccess


class UserService(Service):
    def __init__(self, data_access: UserDataAccess):
        self.data_access = data_access

    @ResultToDict()
    def create(self, user_data: dict):
        return self.data_access.create(user_data)

    @ResultToDict()
    def get(self, user_id: int):
        return self.data_access.get(user_id)

    def update(self, user_id: int, update: dict):
        return self.data_access.update(user_id, update)

    def delete(self, user_id: int):
        return self.data_access.delete(user_id)
```
## Config

### `user_core_lib.yaml`

```yaml
# @package _global_
core_lib:
  user_core_lib:
    data:
      userdb:
        _target_: core_lib.connection.sql_alchemy_connection_factory.SqlAlchemyConnectionFactory
        config:
            log_queries: false
            create_db: true
            session:
                pool_recycle: 3200
                pool_pre_ping: false
            url:
                file: ${oc.env:USERDB_DB}
                protocol: postgresql
                username: ${oc.env:USERDB_USER}
                password: ${oc.env:USERDB_PASSWORD}
                port: ${oc.env:USERDB_PORT}
                host: ${oc.env:USERDB_HOST}
    cache:
        memory_cache:
            _target_: core_lib.cache.cache_handler_ram.CacheHandlerRam
    client:
      user_client:
        _target_: user_core_lib.UserClient
        base_url: https://example.com/
```

## Main Class
Here you'll have all the `DataAccess`, `Service`,  `Connection`, `Cache` initialized. Which can be further accessed when we initialize the `Core-Lib`.

### `user_core_lib.py`

```python
from omegaconf import DictConfig

from core_lib.client.client_base import ClientBase
from core_lib.core_lib import CoreLib
from core_lib.helpers.config_instances import instantiate_config

from user_core_lib.data_layers.data_access.user_data_access import UserDataAccess
from user_core_lib.data_layers.service.user_service import UserService


class UserClient(ClientBase):
    """Returns app-level dicts so callers don't unwrap Response objects."""
    def get(self, user_id: int) -> dict:
        return self._get(f'/user/{user_id}').json()

    def create(self, data: dict) -> dict:
        return self._post('/user', data).json()

    def update(self, user_id: int, data: dict) -> dict:
        return self._put(f'/user/{user_id}', data).json()

    def delete(self, user_id: int) -> None:
        self._delete(f'/user/{user_id}')


class UserCoreLib(CoreLib):
    def __init__(self, conf: DictConfig):
        super().__init__()
        self.config = conf
        CoreLib.cache_registry.register(
            "memory_cache",
            instantiate_config(conf.core_lib.user_core_lib.cache.memory_cache),
        )
        db_session = instantiate_config(conf.core_lib.user_core_lib.data.userdb)
        self.user = UserService(UserDataAccess(db_session))
        self.user_client = instantiate_config(conf.core_lib.user_core_lib.client.user_client)
```

## Initializing
For initializing our `Core-Lib` and mocking the Client we will make use of a test config file that will override the main config file of our `Core-Lib`.


The override drops in two replacements: SQLite for the database, and a Python mock for the HTTP client. The key paths under `core_lib:` **must match the main config exactly** — Hydra merges by path, so a typo here means the override silently doesn't apply.

### `test_config_override.yaml`

```yaml
# @package _global_
core_lib:
  user_core_lib:
    data:
      userdb:
        _target_: core_lib.connection.sql_alchemy_connection_factory.SqlAlchemyConnectionFactory
        config:
          log_queries: false
          create_db: true
          url:
            protocol: sqlite     # in-memory SQLite instead of Postgres
    client:
      user_client:
        _target_: tests.test_user.UserClientMock   # mock instead of real HTTP client
        base_url: https://example.com/
```

### `test_config.yaml`

```yaml
defaults:
  - user_core_lib
  - test_config_override
hydra:
  run:
    dir: .
```

The test file uses an in-memory mock that returns the same shape of dict the real `UserClient` would return. Otherwise the test would fail at `user_data['id']` because `pass` returns `None`.

### `tests/test_user.py`

```python
import unittest
from core_lib.client.client_base import ClientBase
from core_lib.error_handling.status_code_exception import StatusCodeException
from core_lib.helpers.test import load_core_lib_config
from user_core_lib.user_core_lib import UserCoreLib


class UserClientMock(ClientBase):
    """In-memory mock. Same method shapes as UserClient — but no network."""
    _store: dict = {}
    _next_id: int = 1

    def __init__(self, base_url):
        super().__init__(base_url)

    def create(self, data: dict) -> dict:
        record = {'id': UserClientMock._next_id, **data}
        UserClientMock._store[record['id']] = record
        UserClientMock._next_id += 1
        return record

    def get(self, user_id: int) -> dict:
        return UserClientMock._store.get(user_id)

    def update(self, user_id: int, data: dict) -> dict:
        UserClientMock._store[user_id].update(data)
        return UserClientMock._store[user_id]

    def delete(self, user_id: int) -> None:
        UserClientMock._store.pop(user_id, None)


class TestUserCoreLib(unittest.TestCase):

    def setUp(self):
        config = load_core_lib_config('./tests/config', 'test_config.yaml')
        self.core_lib = UserCoreLib(config)

    def test_user_service_round_trip(self):
        # Goes through the real UserService + UserDataAccess against SQLite.
        created = self.core_lib.user.create({'name': 'John', 'contact': '123456'})
        user_id = created['id']

        self.core_lib.user.update(user_id, {'name': 'John Doe'})

        fetched = self.core_lib.user.get(user_id)
        self.assertEqual(fetched['name'], 'John Doe')
        self.assertEqual(fetched['contact'], '123456')

        self.core_lib.user.delete(user_id)
        with self.assertRaises(StatusCodeException):
            self.core_lib.user.get(user_id)

    def test_external_client_is_mocked(self):
        # Uses UserClientMock — no network call.
        created = self.core_lib.user_client.create({'name': 'Jane', 'contact': '999'})
        self.assertEqual(self.core_lib.user_client.get(created['id'])['name'], 'Jane')
```

`load_core_lib_config('./tests/config', 'test_config.yaml')` reads `test_config.yaml`, which composes `user_core_lib.yaml` first then layers `test_config_override.yaml` on top. The SQLite URL and the mock target win. `create_db: true` means SQLAlchemy creates the tables on first connection — no migrations, no fixtures, no Docker.

## Testing Multiple Services with a Shared Instance

When you have multiple test files covering different services, recreating `Core-Lib` in every `setUp()` is slow and resets shared state. Instead, create a singleton instance once and reuse it across all test files.

### `utils.py`

```python
import os
import threading
import traceback

import hydra
from dotenv import load_dotenv
from hydra.core.global_hydra import GlobalHydra

from core_lib.core_lib import CoreLib
from user_core_lib.user_core_lib import UserCoreLib

threadLock = threading.Lock()

class _Instance(object):
    instance = None
    config = None


def load_config():
    if not _Instance.config:
        path = os.path.join(os.path.dirname(__file__), '..', 'data')
        load_dotenv(dotenv_path=os.path.join(path, '.env'))
        GlobalHydra.instance().clear()
        hydra.initialize(config_path=os.path.join('..', 'config'), caller_stack_depth=1)
        _Instance.config = hydra.compose('config.yaml')
    return _Instance.config


def get_core_lib() -> UserCoreLib:
    threadLock.acquire()
    try:
        if not _Instance.instance:
            [CoreLib.cache_registry.unregister(key) for key in CoreLib.cache_registry.registered()]
            [CoreLib.observer_registry.unregister(key) for key in CoreLib.observer_registry.registered()]
            _Instance.instance = UserCoreLib(load_config())
            _Instance.instance.start_core_lib()
        for key in CoreLib.cache_registry.registered():
            CoreLib.cache_registry.get(key).flush_all()
    except BaseException as e:
        print(''.join(traceback.format_exception(type(e), e, e.__traceback__)))
        raise e
    finally:
        threadLock.release()
    return _Instance.instance
```

Each test file calls `get_core_lib()` in `setUp()` — the instance is created once and the cache is flushed between tests.

### `test_user.py`

```python
import unittest
from tests.data.helpers.utils import get_core_lib

class TestUserService(unittest.TestCase):

    def setUp(self):
        self.core_lib = get_core_lib()

    def test_user_service(self):
        pass
```

### `test_customer.py`

```python
import unittest
from tests.data.helpers.utils import get_core_lib

class TestCustomerService(unittest.TestCase):

    def setUp(self):
        self.core_lib = get_core_lib()

    def test_customer_service(self):
        pass
```

If you want to check out more usages of `Core-Lib` you can check out our [examples on GitHub](https://github.com/shay-te/core-lib){:target="_blank"}.

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/constants.html"><< Previous</a></button>
    <button class="pageNext-btn"><a href="/observer.html">Next >></a></button>
</div>