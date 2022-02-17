---
id: crud
title: CRUD Handler
sidebar_label: CRUD Handler
---

## CRUD
In `Core-Lib`, we have classes that can handle CRUD  ( Create, Read, Update, Delete ) for us.
They are as follows



### CRUD
This class is used to initialize `CRUD` with database objects, rule validators and database handlers. It is the Base
class for other classes responsible for CRUD
```python
class CRUD(ABC):

    def __init__(self, db_entity, db: SqlAlchemyDataHandlerRegistry, rule_validator: RuleValidator):
        self._db_entity = db_entity
        self._db = db
        self._rule_validator = rule_validator
```
`db_entity` is the database class or object to be passed for initialization.

`db` is the `SqlAlchemyDataHandlerRegistry` instance used to connect to the database.

`rule_validator` rules must be created with `RuleValidator` and passed.

#### Functions provided by `CRUD`

- `get()` is overridden by other CRUD classes for implementing the function as per their needs.


- `delete()` is overridden by other CRUD classes for implementing the function as per their needs.


- `create()` is used to add a new entry to the database, this function takes a `dict` with the data to be added to the database.
```python
def create(self, data: dict):
```
`data` is type `dict`, key-values pair where key is the column name and value is the entry to be added to the column.


- `update()` is used to update a column in database, This function takes a `dict` that contains the data to be updated 
as well as the `id` of the column that needs to be updated.
```python
def update(self, id: int, data: dict):
```
`id` is type `int`, takes the id of the column to be updated.

`data` is type `dict`, key-values pair where key is the column name and value is the entry to be updated.

### CRUDDataAccess
This class is used to access data via `CRUD` and we have to extend this class to use `CRUD` in your application. This
class is used to initialize `CRUD` and further used to access its functions.

```python
class CRUDDataAccess(DataAccess, CRUD):

    def __init__(self, db_entity, db: SqlAlchemyDataHandlerRegistry, rule_validator: RuleValidator):
        CRUD.__init__(self, db_entity, db, rule_validator)
```
`db_entity` is the database class or object to be passed for initialization.

`db` is the `SqlAlchemyDataHandlerRegistry` instance used to connect to the database.

`rule_validator` rules must be created with `RuleValidator` and passed.

#### Functions provided by `CRUDDataAccess`

- `get()` overrides the function in `CRUD` class, used to get data from database for a given `id`.
```python
def get(self, id: int):
```
`id` is the id of the column we want to query.


- `delete()` overrides the function in `CRUD` class, deletes the data for the given `id`.
```python
def delete(self, id: int):
```
`id` is the id of the column to be deleted.

#### Usage
```python
from core_lib.data_layers.data_access.db.crud.crud import CRUD
from core_lib.data_layers.data_access.db.crud.crud_data_access import CRUDDataAccess
from core_lib.rule_validator.rule_validator import ValueRuleValidator, RuleValidator
from core_lib.data_layers.data.db.sqlalchemy.base import Base
from core_lib.data_transform.result_to_dict import result_to_dict

from sqlalchemy import Column, Integer, VARCHAR, Boolean

class Data(Base):
    __tablename__ = 'user_data'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(VARCHAR(length=255), nullable=False, default="")
    email = Column(VARCHAR(length=255), nullable=False, default="")
    active = Column(Boolean, nullable=False, default="")


class CRUDInit(CRUDDataAccess):
    allowed_update_types = [
        ValueRuleValidator('name', str),
        ValueRuleValidator('email', str),
        ValueRuleValidator('active', bool)
    ]

    rules_validator = RuleValidator(allowed_update_types)

    def __init__(self):
        CRUD.__init__(self, Data, db_handler, CRUDInit.rules_validator)

crud = CRUDInit()

crud.create({'name': 'Jon Doe', 'email': 'abc@def.com', 'active': True})

data = result_to_dict(crud.get(1))
print(data) # {'id': 1, 'name': 'Jon Doe', 'email': 'abc@def.com', 'active': True}

crud.update(1, {'email': 'jon@doe.com'})

data = result_to_dict(crud.get(1))
print(data) # {'id': 1, 'name': 'Jon Doe', 'email': 'jon@doe.com', 'active': True}

crud.delete(1)

data = crud.get(1) # will raise StatusCodeException Not found
```


### CRUDSoftDeleteDataAccess
This class is similar to `CRUDDataAccess` but is used to access and handle soft delete and soft deleted data.
For this to work the database object class must extend `SoftDeleteMixin` to create the required columns for soft delete.

```python
class CRUDSoftDeleteDataAccess(DataAccess, CRUD):

    def __init__(self, db_entity, db: SqlAlchemyDataHandlerRegistry, rule_validator: RuleValidator):
        CRUD.__init__(self, db_entity, db, rule_validator)
```
`db_entity` is the database class or object to be passed for initialization.

`db` is the `SqlAlchemyDataHandlerRegistry` instance used to connect to the database.

`rule_validator` rules must be created with `RuleValidator` and passed.

#### Functions provided by `CRUDSoftDeleteDataAccess`

- `get()` overrides the function in `CRUD` class, used to get data from database for a given `id`.
```python
def get(self, id: int):
```
`id` is the id of the column we want to query.


- `delete()` overrides the function in `CRUD` class, soft deletes the data for the given `id`.
```python
def delete(self, id: int):
```
`id` is the id of the column to be soft deleted.

#### Usage
```python
from core_lib.data_layers.data_access.db.crud.crud import CRUD
from core_lib.data_layers.data_access.db.crud.crud_soft_data_access import CRUDSoftDeleteDataAccess
from core_lib.rule_validator.rule_validator import ValueRuleValidator, RuleValidator
from core_lib.data_layers.data.db.sqlalchemy.base import Base
from core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_mixin import SoftDeleteMixin
from core_lib.data_transform.result_to_dict import result_to_dict

from sqlalchemy import Column, Integer, VARCHAR, Boolean

class DataSoftDelete(Base, SoftDeleteMixin):
    __tablename__ = 'user_data'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(VARCHAR(length=255), nullable=False, default="")
    email = Column(VARCHAR(length=255), nullable=False, default="")
    active = Column(Boolean, nullable=False, default="")


class CRUDSoftDeleteInit(CRUDSoftDeleteDataAccess):
    allowed_update_types = [
        ValueRuleValidator('name', str),
        ValueRuleValidator('email', str),
        ValueRuleValidator('active', bool)
    ]

    rules_validator = RuleValidator(allowed_update_types)

    def __init__(self):
        CRUD.__init__(self, DataSoftDelete, db_handler, CRUDSoftDeleteInit.rules_validator)
crud = CRUDSoftDeleteInit()

crud.create({'name': 'Jon Doe', 'email': 'abc@def.com', 'active': True})

data = result_to_dict(crud.get(1))
print(data) # {'id': 1, 'name': 'Jon Doe', 'email': 'abc@def.com', 'active': True, 'created_at': 'current_timestamp' , 'updated_at': 'current_timestamp', 'deleted_at': None}

crud.update(1, {'email': 'jon@doe.com'})

data = result_to_dict(crud.get(1))
print(data) # {'id': 1, 'name': 'Jon Doe', 'email': 'jon@doe.com', 'active': True, 'created_at': 'created_timestamp' , 'updated_at': 'current_timestamp', 'deleted_at': None}

crud.delete(1) # will update the updated_at and deleted_at columns in the db with current timestamp

data = crud.get(1) # will raise StatusCodeException Not found
```


### CRUDSoftDeleteWithTokenDataAccess
This class is similar to `CRUDSoftDeleteDataAccess` but is uses `SoftDeleteMixin` as well as `SoftDeleteTokenMixin` which
creates the `delete_token` column, if someone wants to index the deleted columns then this class will be used, as 
`delete_token` is type `int` it can be used for indexing.

```python
class CRUDSoftDeleteWithTokenDataAccess(DataAccess, CRUD):

    def __init__(self, db_entity, db: SqlAlchemyDataHandlerRegistry, rule_validator: RuleValidator):
        CRUD.__init__(self, db_entity, db, rule_validator)
```
`db_entity` is the database class or object to be passed for initialization.

`db` is the `SqlAlchemyDataHandlerRegistry` instance used to connect to the database.

`rule_validator` rules must be created with `RuleValidator` and passed.

#### Functions provided by `CRUDSoftDeleteWithTokenDataAccess`

- `get()` overrides the function in `CRUD` class, used to get data from database for a given `id`.
```python
def get(self, id: int):
```
`id` is the id of the column we want to query.


- `delete()` overrides the function in `CRUD` class, soft deletes the data for the given `id`.
```python
def delete(self, id: int):
```
`id` is the id of the column to be soft deleted and also will update the `delete_token` with the current `milliseconds`.

#### Usage
```python
from core_lib.data_layers.data_access.db.crud.crud import CRUD
from core_lib.data_layers.data_access.db.crud.crud_soft_delete_token_data_access import CRUDSoftDeleteWithTokenDataAccess
from core_lib.rule_validator.rule_validator import ValueRuleValidator, RuleValidator
from core_lib.data_layers.data.db.sqlalchemy.base import Base
from core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_mixin import SoftDeleteMixin
from core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_token_mixin import SoftDeleteTokenMixin
from core_lib.data_transform.result_to_dict import result_to_dict

from sqlalchemy import Column, Integer, VARCHAR, Boolean

class DataSoftDeleteToken(Base, SoftDeleteMixin, SoftDeleteTokenMixin):
    __tablename__ = 'user_data'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(VARCHAR(length=255), nullable=False, default="")
    email = Column(VARCHAR(length=255), nullable=False, default="")
    active = Column(Boolean, nullable=False, default="")


class CRUDSoftDeleteTokenInit(CRUDSoftDeleteWithTokenDataAccess):
    allowed_update_types = [
        ValueRuleValidator('name', str),
        ValueRuleValidator('email', str),
        ValueRuleValidator('active', bool)
    ]

    rules_validator = RuleValidator(allowed_update_types)

    def __init__(self):
        CRUD.__init__(self, DataSoftDeleteToken, db_handler, CRUDSoftDeleteTokenInit.rules_validator)

crud = CRUDSoftDeleteTokenInit()

crud.create({'name': 'Jon Doe', 'email': 'abc@def.com', 'active': True})

data = result_to_dict(crud.get(1))
print(data) # {'id': 1, 'name': 'Jon Doe', 'email': 'abc@def.com', 'active': True, 'created_at': 'current_timestamp' , 'updated_at': 'current_timestamp', 'deleted_at': None, 'delete_token': None}

crud.update(1, {'email': 'jon@doe.com'})

data = result_to_dict(crud.get(1))
print(data) # {'id': 1, 'name': 'Jon Doe', 'email': 'jon@doe.com', 'active': True, 'created_at': 'created_timestamp' , 'updated_at': 'current_timestamp', 'deleted_at': None, 'delete_token': None}

crud.delete(1) # will update the updated_at and deleted_at columns in the db with current timestamp and will update the delete_token with timestamp in milliseconds

data = crud.get(1) # will raise StatusCodeException Not found
```