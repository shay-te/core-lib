---
id: soft_delete
title: Soft Delete Handler
sidebar_label: Soft Delete Handler
---

# Soft Delete
In `Core-Lib`, the classes `SoftDeleteMixin` and `SoftDeleteTokenMixin` handle soft deletes. These two classes can be imported 
and passed to a `SQLAlchemy` Base class to create the appropriate soft delete fields.

## SoftDeleteMixin

*core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_mixin.SoftDeleteMixin* [[source]](https://github.com/shay-te/core-lib/blob/5b8b2a4ca73dfd29138a216eb1f5648a5ae9be55/core_lib/data_layers/data/db/sqlalchemy/mixins/soft_delete_mixin.py#L6)

`SoftDeleteMixin` creates the following columns in a table.
- `created_at`:
  - type: `DateTime`
  - default: `datetime.utcnow`


- `updated_at`:
  - type: `DateTime`
  - default: `datetime.utcnow`
  - onupdate: `datetime.utcnow` immediately updates when the system changes the value of `deleted_at`.


- `deleted_at`:
  - type: `DateTime`
  - default: `None`
  - When a user wishes to execute a soft deletion on a column, this field must be updated by the value `datetime.utcnow`.

```python
class SoftDeleteMixin(object):
    created_at = Column(DateTime, default=datetime.utcnow)
    created_at._creation_order = 9998
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_at._creation_order = 9998
    deleted_at = Column(DateTime, default=None)
    deleted_at._creation_order = 9998
```


## SoftDeleteTokenMixin

*core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_token_mixin.SoftDeleteTokenMixin* [[source]](https://github.com/shay-te/core-lib/blob/5b8b2a4ca73dfd29138a216eb1f5648a5ae9be55/core_lib/data_layers/data/db/sqlalchemy/mixins/soft_delete_token_mixin.py#L4)

`SoftDeleteTokenMixin` creates the following column in a table. Which can be used for Indexing, If the user wants the 
`deleted_at` column to be indexed, it's best to use `delete_token` because indexing on a `DateTime` column is slow.
>**Note:** If the user does not want indexing on `deleted_at`, this class can be skipped and the `delete_token` column will not be created. 
- `delete_token`:
  - type: `Integer`
  - default: `None`
  - When a user updates the `deleted_at` column, `delete_token` should also be updated with the value `int(datetime.utcnow)`
  to store the Integer value of the current timestamp which can be used for indexing.

```python
class SoftDeleteTokenMixin(object):
    delete_token = Column(Integer, default=None)
    delete_token._creation_order = 9998
```


### Example
```python
from core_lib.data_layers.data.db.sqlalchemy.base import Base
from core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_mixin import SoftDeleteMixin
from core_lib.data_layers.data.db.sqlalchemy.mixins.soft_delete_token_mixin import SoftDeleteTokenMixin

from sqlalchemy import Integer, Column, VARCHAR
from datetime import datetime

class Data(Base, SoftDeleteMixin, SoftDeleteTokenMixin):

    __tablename__ = 'user_data'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(VARCHAR(length=255), nullable=False, default="")
# creates a table with the column
# id, name, updated_at, created_at, deleted_at and deleted_at_token

.
.
.
def delete_user():
    # to carry out soft delete, once the deleted_at column is set we know the value is deleted from client side.
    session.query(Data).filter(Data.id == 1).update({'deleted_at': datetime.utcnow(), 'deleted_at_token':  int(datetime.utcnow().timestamp())})

```