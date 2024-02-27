---
id: test_core_lib
title: Testing Core Lib
sidebar: core_lib_doc_sidebar
permalink: test_core_lib.html
folder: core_lib_doc
toc: false
---

Let's understand how `Core-Lib` is initialized and tested and how to integrate it with your new or existing application.


## DataAccess
The `DataAccess` layer is the facade of the data layer, consisting of `API` functions that will access our data sources, such as database connections and entities.

`user_data_access.py`
```python
from http import HTTPStatus

from core_lib.data_layers.data_access.db.crud.crud_data_access import CRUDDataAccess
from core_lib.connection.sql_alchemy_connection_registry import SqlAlchemyConnectionRegistry
from core_lib.error_handling.status_code_exception import StatusCodeException
from user_core_lib.data_layers.data.db.user import User
from core_lib.error_handling.not_found_decorator import NotFoundErrorHandler


class UserDataAccess(CRUDDataAccess):
    def __init__(self, db: SqlAlchemyConnectionRegistry):
        CRUD.__init__(self, User, db)
```

## Service 
The `Service` layer is a facade of the `DataAccess` layer and connections. consisting of `API` functions that will handle business logic, data transformation, and caching.

`user_service.py`
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
`user_core_lib.yaml`
```yaml
# @package _global_
core_lib:
  user_core_lib:
    data:
      userdb:
        _target_: core_lib.connection.sql_alchemy_connection_registry.SqlAlchemyConnectionRegistry
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
Here you'll have all the `DataAccess`, `Service`,  `Connection`, and `Cache` initialized. Which can be further accessed when we initialize the `Core-Lib`.

`user_core_lib.py`
```python
from omegaconf import DictConfig

from core_lib.core_lib import CoreLib
from core_lib.connection.sql_alchemy_connection_registry import SqlAlchemyConnectionRegistry
from core_lib.helpers.config_instances import instantiate_config

from user_core_lib.data_layers.data_access.customer_data_access import CustomerDataAccess
from user_core_lib.data_layers.data_access.user_data_access import UserDataAccess
from user_core_lib.data_layers.service.customer_service import CustomerService
from user_core_lib.data_layers.service.user_service import UserService

class UserClient(ClientBase):
    def __init__(self, target_url):
        ClientBase.__init__(self, target_url)

    def get(self, user_id: int):
        return self._get(f'/user/{user_id}')
    
    def create(self, data: dict):
        return self._post(f'/create_user', data)
    
    def update(self, data: dict):
        return self._put(f'/update_user', data)
    
    def delete(self, user_id: int):
        return self._delete(f'/user/{user_id}')

class UserCoreLib(CoreLib):
    def __init__(self, conf: DictConfig):
        super().__init__()
        self.config = conf
        CoreLib.cache_registry.register("memory_cache", instantiate_config(self.config.core_lib.user_core_lib.cache.memory_cache))
        db_session = instantiate_config(self.config.core_lib.user_core_lib.data.userdb)
        self.user = UserService(UserDataAccess(db_session))
        self.user_client = instantiate_config(self.config.core_lib.user_core_lib.client.user_client)
```

## Initializing
For initializing our `Core-Lib` and mocking the Client we will make use of a test config file that will override the main config file of our `Core-Lib`.


This config will override the `UserClient` config with the `UserClientMock`.
`test_config_override.yaml`
```yaml
# @package _global_
core_lib:
  user_core_lib:
    userdb:
        _target_: core_lib.connection.sql_alchemy_connection_registry.SqlAlchemyConnectionRegistry
        config:
            log_queries: false
            create_db: true
            session:
                pool_recycle: 3200
                pool_pre_ping: false
            url:
                protocol: sqlite
    client:
      user_client:
        _target_: test.UserClientMock
        base_url: https://example.com/
```

`test_config.yaml`
```yaml
defaults:
 - user_core_lib
 - test_config_override
 hydra:
  run:
    dir: .
```

In your test file

`test.py`
```python
import unittest

from core_lib.error_handling.status_code_exception import StatusCodeException
from user_core_lib.user_core_lib import UserCoreLib
from core_lib.helpers.test import load_core_lib_config
from core_lib.client.client_base import ClientBase
from core_lib.helpers.config_instances import instantiate_config

class UserClientMock(ClientBase):
    def __init__(self, target_url):
        ClientBase.__init__(self, target_url)

    def get(self, user_id: int):
        pass
    
    def create(self, data: dict):
        pass
    
    def update(self, data: dict, user_id: int):
        pass
    
    def delete(self, user_id: int):
        pass

class TestCoreLib(unittest.TestCase):
    
    def setUp(self):
        # util that will clear all the earlier Core-Lib data and return DictConfig
        self.config = load_core_lib_config('./test/config', 'test_config.yaml')
        # here we initialize the Core-Lib
        self.user_core_lib = UserCoreLib(self.config)
    
    
    def test_core_lib(self):
        user_data = self.user_core_lib.user.create({'name': 'John', 'contact': '123456'}) # store the created data to retrieve the id for update and delete 
        user_id = user_data['id']
        self.assertEqual(user_data['name'], 'John')
        self.assertEqual(user_data['contact'], '123456')
        
        self.user_core_lib.user.update(user_id, {'name': 'John Doe', 'contact': '789456'})
        
        user_data = self.user_core_lib.user.get(user_id) # returns the data at the specified id or raises exception if id not found
        self.assertEqual(user_data['name'], 'John Doe')
        self.assertEqual(user_data['contact'], '789456')
        
        self.user_core_lib.user.delete(user_id) # deletes the entry at the specified id
        with self.assertRaises(StatusCodeException):
            self.user_core_lib.user.get(user_id)

    def test_client(self):
        # loads the UserClientMock instance
        user_client = self.user_core_lib.user_client
        user_data = user_client.create({'name': 'John', 'contact': '123456'})
        user_id = user_data['id']
        self.assertEqual(user_data['name'], 'John')
        self.assertEqual(user_data['contact'], '123456')
        
        user_client.update(user_id, {'name': 'John Doe', 'contact': '789456'})
        
        user_data = user_client.get(user_id) 
        self.assertEqual(user_data['name'], 'John Doe')
        self.assertEqual(user_data['contact'], '789456')
        
        user_client.delete(user_id)

```

This is a basic usage of how to initialize and test a `Core-Lib` and write `DataAccess` and `Service`. Once a `Core-Lib` instance is created, you can pass it on to different files and keep this instance singleton so the data in the `cache` and `registry` remains persistent. Make sure to initialize it at the topmost level of your application.

## When Multiple Services are to be tested:

- In this case, we can `create a singleton core-lib instance and use it to test all services`.

`utils.py`
```python
import os
import threading
import traceback

import hydra
from dotenv import load_dotenv
from hydra.core.global_hydra import GlobalHydra

from user_core_lib.user_core_lib import UserCoreLib
from user_core_lib_instance import UserCoreLibInstance
from core_lib.core_lib import CoreLib

threadLock = threading.Lock()

class UserInstange(object):
    instance = None
    config = None


def load_config():
    if not UserInstange.config:
        path = os.path.join(os.path.dirname(__file__), '..', 'data')
        load_dotenv(dotenv_path=os.path.join(path, '.env'))

        GlobalHydra.instance().clear()
        hydra.initialize(config_path=os.path.join('..', 'config'), caller_stack_depth=1)
        UserInstange.config = hydra.compose('config.yaml')
    return UserInstange.config


def sync_create_start_core_lib() -> UserCoreLib:
    threadLock.acquire()
    if not UserInstange.instance:
        try:
            [CoreLib.cache_registry.unregister(key) for key in CoreLib.cache_registry.registered()]
            [CoreLib.observer_registry.unregister(key) for key in CoreLib.observer_registry.registered()]
            UserCoreLibInstance.init(load_config())
            UserInstange.instance = AdminCoreLibInstance.get()
            UserInstange.instance.start_core_lib()
        except BaseException as e:
            print(''.join(traceback.format_exception(type(e), e, e.__traceback__)))
            raise e

    # Clear the cache
    for key in CoreLib.cache_registry.registered():
        CoreLib.cache_registry.get(key).flush_all()


    threadLock.release()
    return UserInstange.instance

```
#### Global Variables and Classes:

- **`threadLock`**: A threading lock to prevent race conditions when accessing shared resources.
- **`UserInstange`**: A class that manages a singleton instance of UserCoreLib.
    - **`instance`**: Variable to hold the singleton instance of UserCoreLib.
    - **`config`**: Variable to hold the configuration data.

#### Function load_config():
- This function loads the configuration data from a `.env` file and a `config.yaml` file using `Hydra`.
- It returns the loaded configuration.

#### Function sync_create_start_core_lib():
- This function is responsible for creating and starting the `UserCoreLib` instance.
- It first acquires the thread lock to ensure that only one thread executes this block of code at a time.
- If the `UserInstange.instance` is not set (i.e., the UserCoreLib instance has not been created yet):
    - It clears any existing registrations from the `CoreLib.cache_registry` and `CoreLib.observer_registry`.
    - Initializes the `AdminCoreLibInstance` with the loaded configuration.
    - Starts the `UserCoreLib` instance.
    - If an exception occurs during this process, it prints the traceback and re-raises the exception.
- After creating the instance, it clears the cache of `CoreLib.cache_registry`.
- Finally, it releases the thread lock and returns the `UserInstange.instance`.

### For Example, You need to create 3 Services having names:
- UserService
- CustomerService
- NotificationService

`test_user.py`
```python
import unittest

from tests.data.helpers.utils import sync_create_start_core_lib

class TestCoreLib(unittest.TestCase):
    
    def setUp(self):
        # here we get an already initialized Core-Lib
        self.user_core_lib = sync_create_start_core_lib()
    
    
    def test_user_service(self):
        # testing everything realted to user_service
        pass
```

`test_customer.py`
```python
import unittest

from tests.data.helpers.utils import sync_create_start_core_lib

class TestCoreLib(unittest.TestCase):
    
    def setUp(self):
        # here we get an already initialized Core-Lib
        self.user_core_lib = sync_create_start_core_lib()
    
    
    def test_customer_service(self):
        # testing everything realted to customer_service
        pass
```

`test_notification.py`
```python
import unittest

from tests.data.helpers.utils import sync_create_start_core_lib

class TestCoreLib(unittest.TestCase):
    
    def setUp(self):
        # here we get an already initialized Core-Lib
        self.user_core_lib = sync_create_start_core_lib()
    
    
    def test_notification_service(self):
        # testing everything realted to notification_service
        pass
```
