---
id: crud
title: CRUD Handler
sidebar_label: CRUD Handler
---

## CRUD
`Core-Lib` provides `CRUD ( Create, Read, Update, Delete )` `DataAccess` classes as boilerplate code.

They are as follows



### CRUD
This class is used to initialize `CRUD` with database objects, rule validators and database handlers. `CRUD` is an abstract base class for all types of `CRUDDataAccess` in `Core-Lib`.
```python
class CRUD(ABC):

    def __init__(self, db_entity, db: SqlAlchemyDataHandlerRegistry, rule_validator: RuleValidator = None):
        self._db_entity = db_entity
        self._db = db
        self._rule_validator = rule_validator
```
`db_entity` the database entity used by this `DataAccesss`.

`db` instance of the `SqlAlchemyDataHandlerRegistry` used to connect to the database.

`rule_validator` uses the `RuleValidator` instance to validate data passed into `create()` and `update()` methods (optional).

#### Functions provided by `CRUD`

- `get(id: int)` an abstract method to be implemented with `DataAccess` subclasses


- `delete(id: int)` an abstract method to be implemented with `DataAccess` subclasses.


- `create(data: dict)` is used to add a new entry into the database, this function takes a `dict` with the data to be added to the database.
```python
def create(self, data: dict):
```
`data` is type `dict`, key-values pair where key is the column name and value is the entry to be added to the column.


- `update(id: int, data: dict)` used to update data in the database. This function takes a `dict` that contains the data to be updated 
as well as the `id` of the column that needs to be updated.
```python
def update(self, id: int, data: dict):
```
`id` is type `int`, takes the id of the column to be updated.

`data` is type `dict`, key-values pair where key is the column name and value is the entry to be updated.

### CRUDDataAccess
Extends the class `CRUD` and implements the `get()` and `delete()` methods

```python
class CRUDDataAccess(DataAccess, CRUD):

    def __init__(self, db_entity, db: SqlAlchemyDataHandlerRegistry, rule_validator: RuleValidator):
        CRUD.__init__(self, db_entity, db, rule_validator)
```


#### Functions provided by `CRUDDataAccess`

- `get(id: int)` overrides the function in `CRUD` class, used to get data from database for a given `id`.
```python
def get(self, id: int):
```
`id` is the id of the column we want to query.


- `delete(id: int)` overrides the function in `CRUD` class, deletes the data for the given `id`.
```python
def delete(self, id: int):
```
`id` is the id of the column to be deleted.

#### Usage
```python
from core_lib.data_layers.data_access.db.crud.crud import CRUD
from core_lib.data_layers.data_access.db.crud.crud_data_access import CRUDDataAccess
from core_lib.data_layers.data.db.sqlalchemy.base import Base

from sqlalchemy import Column, Integer, VARCHAR, Boolean

class Customer(Base):
    __tablename__ = 'customer_data'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(VARCHAR(length=255), nullable=False, default="")
    email = Column(VARCHAR(length=255), nullable=False, default="")
    active = Column(Boolean, nullable=False)


class CustomerCRUDDataAccess(CRUDDataAccess):
    def __init__(self):
        CRUD.__init__(self, Customer, db_handler)

```


### CRUDSoftDeleteDataAccess
Similar to `CRUDDataAccess` but is used to access and handle soft delete.
For this to work the database object class must extend `SoftDeleteMixin` to create the required columns for soft delete.

```python
class CRUDSoftDeleteDataAccess(DataAccess, CRUD):

    def __init__(self, db_entity, db: SqlAlchemyDataHandlerRegistry, rule_validator: RuleValidator):
        CRUD.__init__(self, db_entity, db, rule_validator)
```


#### Functions provided by `CRUDSoftDeleteDataAccess`

- `get(id: int)` overrides the function in `CRUD` class, used to get data from database for a given `id` where `deleted_at` is `None`.
```python
def get(self, id: int):
```
`id` is the id of the column we want to query.


- `delete(id: int)` overrides the function in `CRUD` class, soft deletes the data for the given `id`, `SoftDeleteMixin` will set the `deleted_at` to current timestamp.
```python
def delete(self, id: int):
```
`id` is the id of the column to be soft deleted.

#### Usage
```python
from core_lib.data_layers.data_access.db.crud.crud import CRUD
from core_lib.data_layers.data_access.db.crud.crud_soft_data_access import CRUDSoftDeleteDataAccess
from core_lib.data_layers.data.db.sqlalchemy.base import Base
from core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_mixin import SoftDeleteMixin

from sqlalchemy import Column, Integer, VARCHAR, Boolean

class Customer(Base, SoftDeleteMixin):
    __tablename__ = 'customer_data'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(VARCHAR(length=255), nullable=False, default="")
    email = Column(VARCHAR(length=255), nullable=False, default="")
    active = Column(Boolean, nullable=False)


class CustomerCRUDSoftDeleteDataAccess(CRUDSoftDeleteDataAccess):

    def __init__(self):
        CRUD.__init__(self, Customer, db_handler)

```


### CRUDSoftDeleteWithTokenDataAccess
This class is similar to `CRUDSoftDeleteDataAccess` but is uses `SoftDeleteMixin` as well as `SoftDeleteTokenMixin` which
creates the `delete_token` column, because indexing a `DateTime` column is slow, adding the `delete_token` allows us to index the columns that have been deleted.

```python
class CRUDSoftDeleteWithTokenDataAccess(DataAccess, CRUD):

    def __init__(self, db_entity, db: SqlAlchemyDataHandlerRegistry, rule_validator: RuleValidator):
        CRUD.__init__(self, db_entity, db, rule_validator)
```


#### Functions provided by `CRUDSoftDeleteWithTokenDataAccess`

- `get()` overrides the function in `CRUD` class, used to get data from database for a given `id` where `deleted_at` is `None`.
```python
def get(self, id: int):
```
`id` is the id of the column we want to query.


- `delete()` overrides the function in `CRUD` class, soft deletes the data for the given `id`, 
`SoftDeleteMixin` will set the `deleted_at` to current timestamp and `SoftDeleteTokenMixin` will set the `delete_token` to `int` value of current timestamp.
```python
def delete(self, id: int):
```
`id` is the id of the column to be soft deleted and also will update the `delete_token` with the current `milliseconds`.

#### Usage
```python
from core_lib.data_layers.data_access.db.crud.crud import CRUD
from core_lib.data_layers.data_access.db.crud.crud_soft_delete_token_data_access import CRUDSoftDeleteWithTokenDataAccess
from core_lib.data_layers.data.db.sqlalchemy.base import Base
from core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_mixin import SoftDeleteMixin
from core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_token_mixin import SoftDeleteTokenMixin

from sqlalchemy import Column, Integer, VARCHAR, Boolean

class Customer(Base, SoftDeleteMixin, SoftDeleteTokenMixin):
    __tablename__ = 'customer_data'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(VARCHAR(length=255), nullable=False, default="")
    email = Column(VARCHAR(length=255), nullable=False, default="")
    active = Column(Boolean, nullable=False)


class CustomerCRUDSoftDeleteWithTokenDataAccess(CRUDSoftDeleteWithTokenDataAccess):
    def __init__(self):
        CRUD.__init__(self, Customer, db_handler)

```

### Example for CRUD
Implementation with SoftDelete and SoftDeleteToken
```python
from core_lib.data_layers.data_access.db.crud.crud import CRUD
from core_lib.data_layers.data_access.db.crud.crud_soft_delete_token_data_access import CRUDSoftDeleteWithTokenDataAccess
from core_lib.rule_validator.rule_validator import ValueRuleValidator, RuleValidator
from core_lib.data_layers.data.db.sqlalchemy.base import Base
from core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_mixin import SoftDeleteMixin
from core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_token_mixin import SoftDeleteTokenMixin
from core_lib.data_transform.result_to_dict import result_to_dict

from sqlalchemy import Column, Integer, VARCHAR, Boolean

class Customer(Base, SoftDeleteMixin, SoftDeleteTokenMixin):
    __tablename__ = 'customer_data'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(VARCHAR(length=255), nullable=False, default="")
    email = Column(VARCHAR(length=255), nullable=False, default="")
    active = Column(Boolean, nullable=False)


class CustomerCRUDDataAccess(CRUDSoftDeleteWithTokenDataAccess):
    allowed_update_types = [
        ValueRuleValidator('name', str),
        ValueRuleValidator('email', str),
        ValueRuleValidator('active', bool)
    ]

    rules_validator = RuleValidator(allowed_update_types)

    def __init__(self):
        CRUD.__init__(self, Customer, db_handler, CustomerCRUDDataAccess.rules_validator)

customer = CustomerCRUDDataAccess()

customer.create({'name': 'Jon Doe', 'email': 'abc@def.com', 'active': True})

data = result_to_dict(customer.get(1))
print(data) # {'id': 1, 'name': 'Jon Doe', 'email': 'abc@def.com', 'active': True, 'created_at': 'current_timestamp' , 'updated_at': 'current_timestamp', 'deleted_at': None, 'deleted_at_token': None}

customer.update(1, {'email': 'jon@doe.com'})

data = result_to_dict(customer.get(1))
print(data) # {'id': 1, 'name': 'Jon Doe', 'email': 'jon@doe.com', 'active': True, 'created_at': 'created_timestamp' , 'updated_at': 'current_timestamp', 'deleted_at': None, 'deleted_at_token': None}

customer.delete(1) # will update the updated_at and deleted_at columns in the db with current timestamp and will update the deleted_at_token with timestamp in milliseconds

data = customer.get(1) # will raise StatusCodeException Not found
```
