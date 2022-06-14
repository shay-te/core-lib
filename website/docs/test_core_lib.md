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

from core_lib.data_layers.data_access.data_access import DataAccess
from core_lib.connection.sql_alchemy_connection_registry import SqlAlchemyConnectionRegistry
from core_lib.error_handling.status_code_exception import StatusCodeException
from user_core_lib.data_layers.data.db.user import User
from core_lib.error_handling.not_found_decorator import NotFoundErrorHandler


class UserDataAccess(DataAccess):
    def __init__(self, db: SqlAlchemyConnectionRegistry):
        self.db = db

    def create(self, user_data: dict):
        with self.db.get() as session:
            user = User(**user_data)
            session.add(user)
        return user

    def update(self, user_id: int, user_data: dict):
        with self.db.get() as session:
            return session.query(User).filter(User.id == user_id).update(user_data)

    def delete(self, id: int):
        with self.db.get() as session:
            return (
                session.query(User)
                .filter(User.id == id)
                .delete()
            )
    @NotFoundErrorHandler()
    def get(self, user_id):
        with self.db.get() as session:
            return session.query(User).get(user_id)
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
```

In your main file

`main.py`
```python
import hydra
from omegaconf import OmegaConf
from core_lib.core_lib import CoreLib

from user_core_lib.user_core_lib import UserCoreLib

# A utility to help us clean all the existing keys, clear registries, clear hydra instances and return the `DictConfig` from the yaml file
# you can keep this utility elsewhere for keep the file clean too
def sync_create_core_lib_config(path: str, config_file):
    [CoreLib.cache_registry.unregister(key) for key in CoreLib.cache_registry.registered()]
    [CoreLib.observer_registry.unregister(key) for key in CoreLib.observer_registry.registered()]
    hydra.core.global_hydra.GlobalHydra.instance().clear()
    hydra.initialize(config_path=path)
    config = hydra.compose(config_file)
    return config

# here we have the config for the Core-Lib
config = sync_create_core_lib_config('./config', 'user_core_lib.yaml')

# here we initialize the Core-Lib
user_core_lib = UserCoreLib(config)
# this will initialize the Core-Lib with the connection and we can access the service to communicate with the database.

user_data = user_core_lib.user.create({'name': 'John', 'contact': '123456'}) # store the created data to retrieve the id for update and delete 
user_id = user_data['id']
# this will call the create function inside the `UserService` and that will call the create() in the `UserDataAccess`, thus creating a new user in the database, while keeping the layers different for clean code.

user_core_lib.update(user_id, {'name': 'John Doe', 'contact': '789456'})

user_core_lib.get(user_id) # returns the data at the specified id or raises exception if id not found

user_core_lib.delete(user_id) # deletes the entry at the specified id
```

This is a basic usage of how to initialize a `Core-Lib` and write `DataAccess` and `Service`. Once a `Core-Lib` instance is created that you can pass it on to different files and keep this instance singleton so the data in the `cache` and `registry` remains persistent. Make sure to initialize it at the topmost level of your application. 

If you want to check out more usages of `Core-Lib` you can check out our examples here.