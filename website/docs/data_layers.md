---
id: data_layers
title: Data Layers
sidebar_label: Data Layers
---

`Service`, `DataAccess` are nothing more the a plain python classes.

Data Layers classes only provide basic task in mind 

```
Keep Data Flow with the SAME rules and architecture.
```

[For more information about Data Lyaers.](#atricle_layers.md)

### Data Layer

In this layer we will define all entities, migration, connectors, mapping, this is the layers define low level assets that needed to connect to various data sources.

##### <project_dir>/data_layers/data/db/user.py

```python
import enum
from core_lib.data_layers.data.db.sqlalchemy.base import Base
from core_lib.data_layers.data.db.sqlalchemy.types.int_enum import IntEnum
from core_lib.data_layers.data.db.sqlalchemy.mixins.time_stamp_mixin import TimeStampMixin
from sqlalchemy import Column, Integer, VARCHAR


class User(TimeStampMixin, Base):

    __tablename__ = 'user'

    class Gender(enum.Enum):
        FEMALE = enum.auto()
        MALE  = enum.auto()

    id           = Column(Integer, primary_key=True, nullable=False)
    email        = Column(VARCHAR(length=255), nullable=False)
    gender       = Column('gender', IntEnum(Gender))
	...
```

Migration example with alembic how to load the application configuration please.

### Data Access Layer

Here we will expose our Product! data API .

#### Responsibilities: 

1. Expose the Product data API. 
2. Optimization and speed.
3. Caching

```python
class UserDataAccess(DataAccess):

    def __init__(self, data_sessions: list):
        DataAccess.__init__(self, data_sessions)
        self.logger = logging.getLogger(str(UserDataAccess))

    def get(self, id: int):
        with self.get_session(DBDataSessionFactory.name) as session:
            return session.Query(User).get(id)
```

### Service Layer

#### Responsibilities: 

1. Business Logic
2. Transform all get data into `dict`
3. Caching

```python
from core_lib.data_transform.result_to_dict import ResultToDict
from core_lib.data_layers.service.service import Service

class UserService(Service):

    def __init__(self, user_data_access: UserDataAccess, user_friends_data_acccess: UserFriendsDataAccess):
        self.user_data_access = user_data_access
        self.user_friends_data_acccess = user_friends_data_acccess

    @ResultToDict # Transform data to dict. 
    def get(self, user_id: int):
        user = self.user_data_access.get(user_id)
        if user.something:
            user.friends = self.user_friends_data_acccess.get_user_friends(user_id)
        return user
```


   

## Sample Application

Sample applications can be found here 