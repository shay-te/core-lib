---
id: test_core_lib
title: Test Core Lib
sidebar_label: Test Core Lib
---

Let's understand how `Core-Lib` is initialized and how to integrate it with your new or existing application.

## Main Class
Here you'll have all the `DataAccess`, `Service`,  `Connection`, `Cache` initialized. Which can be further accessed when we initialize the `Core-Lib`.

`user_core_lib.py`
```python
from omegaconf import DictConfig

from core_lib.cache.cache_handler_ram import CacheHandlerRam
from core_lib.core_lib import CoreLib
from core_lib.connection.sql_alchemy_connection_registry import SqlAlchemyConnectionRegistry

from user_core_lib.data_layers.data_access.customer_data_access import CustomerDataAccess
from user_core_lib.data_layers.data_access.user_data_access import UserDataAccess
from user_core_lib.data_layers.service.customer_service import CustomerService
from user_core_lib.data_layers.service.user_service import UserService


class UserCoreLib(CoreLib):
    def __init__(self, conf: DictConfig):
        super().__init__()
        self.config = conf
        CoreLib.cache_registry.register("memory_cache", CacheHandlerRam())
        db_session = SqlAlchemyConnectionRegistry(self.config.core_lib.user_core_lib.data.userdb)
        self.user = UserService(UserDataAccess(db_session))
```

## DataAccess
Here you should define the functions that only and only communicate with the connection created, for e.g., queries to get some data from a database or insert some data in the database, Solr queries or whatever the function has to interface with the connection.

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
Here we right the business logic for the extracted data, as the `DataAccess` only handles the interfacing with the connection, a `Service` will only be used to take the data and process it.

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

## Initializing
For initializing our `Core-Lib` we will need a config that is stored under the config directory.

`user_core_lib.yaml`
```yaml
# @package _global_
core_lib:
  user_core_lib:
    cache:
      memory_cache:
        type: memory
    data:
      userdb:
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
    client:
      user_client:
        _target_: core_lib.client.client_base.ClientBase
        base_url: https://example.com/
```

In your test file

`test.py`
```python
import unittest

from core_lib.error_handling.status_code_exception import StatusCodeException
from user_core_lib.user_core_lib import UserCoreLib
from tests.test_data.test_utils import sync_create_core_lib_config
from core_lib.client.client_base import ClientBase
from core_lib.helpers.config_instances import instantiate_config

class UserClient(ClientBase):
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
        self.config = sync_create_core_lib_config('./config', 'user_core_lib.yaml')
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
    
    # instantiate_config to create a instance of UserClient class
    def test_client(self):
        user_client = instantiate_config(self.config.core_lib.user_core_lib.client.user_client)
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

This is a basic usage of how to initialize and test a `Core-Lib` and write `DataAccess` and `Service`. Once a `Core-Lib` instance is created that you can pass it on to different files and keep this instance singleton so the data in the `cache` and `registry` remains persistent. Make sure to initialize it at the topmost level of your application. 

If you want to check out more usages of `Core-Lib` you can check out our examples here.