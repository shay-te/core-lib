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

## The Folder Structure

Code-Lib recommended Data Structure:

 ``` 
This is how code of Core-Lib is mapped internally. 
Core-Lib can be connected to a network of Core-Lib that can 
easly expand by extending each other pipe-line (Look at the code for combine example)
 ```



```
core_lib // root folder of our library
└─── data_layers
|    └─── data // store all connector, definition, mapping to data sources
|    │    └─── db // store database ORM entities
|    │       └─── migrations // data base migration scripts
|    │    └─── elastic // store elastice search base classes
|    │    // etc..
|    └─── data_access // expose API that uses data layer
|	 |    └─── user // grather data access by user
|	 |    	   └─── user_data_access.py
|	 |    	   └─── user_list_data_access.py
|	 |    └─── some_data_access.py 
|    └─── service // expost the core-lib services
|    core_lib_app.py //The file that glow the entire up togther 
└─── jobs // jobs defenitions
tests // Unit test the enttire data_layers 
```

## Sample Application

Imagine we have application the have the following requirements:

### Data Layer

In this layer we will define all entities, migration, connectors, mapping, this is the layers define low level assets that needed to connect to various data sources.

##### <project_dir>/data_layers/data/db/user.py

```python
import enum
from core_lib.data_layers.data.db.base import Base
from core_lib.data_layers.data.db.enums.int_enum import IntEnum
from core_lib.data_layers.data.db.mixins.time_stamp_mixin import TimeStampMixin
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

    def get_by_id(self, id: int):
        with self.get_session(DBDataSessionFactory.name) as session:
            return session.Query(User).get(id)
```

### Service Layer

#### Responsibilities: 

1. Business Logic
2. Transform all get data into `dict`
3. Caching

```python
from core_lib.data_layers.service.data_transform import ResultToDict
from core_lib.data_layers.service.service import Service

class UserService(Service):

    def __init__(self, user_data_access: UserDataAccess, user_friends_data_acccess: UserFriendsDataAccess):
        self.user_data_access = user_data_access
        self.user_friends_data_acccess = user_friends_data_acccess

    @ResultToDict # Transform data to dict. 
    def get_info(self, user_id: int):
        user = self.user_data_access.get_by_id(user_id)
        if user.something:
            user.friends = self.user_friends_data_acccess.get_user_friends(user_id)
        return user
```

