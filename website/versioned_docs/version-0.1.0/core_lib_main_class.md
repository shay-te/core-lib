---
id: core_lib_main_class
title: Core Lib Class
sidebar_label: Core Lib Class
---

*core_lib.core_lib.CoreLib* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/core_lib.py#L17)

 `CoreLib` class is the main interface to the entire library, it exposes all the "Services" of your library.  

It uses simple assignment of `Services`, ` DataAccess,` and `Clients` to `YourCoreLib` class. You define your library interface. 



## Usage 
```python
from core_lib.core_lib import CoreLib
from core_lib.helpers.config_instances import instantiate_config
...

class YourCoreLib(CoreLib):
    def __init__(self, config: DictConfig):
        CoreLib.__init__(self)
        self.email = instantiate_config(self.config, EmailCoreLib)  # create `EmailCoreLib` instance from config
        user_da = UserDataAccess(instantiate_config(self.config.core_lib.data.db, SqlAlchemyConnectionRegistry))
        self.user = UserService(user_da)
        self.user_photos = UserPhotosService(user_da)        
        ...
```



## init()

*core_lib.core_lib.CoreLib.\_\_init\_\_()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/core_lib.py#L22)

When extending  `CoreLib` class call  `CoreLib.__init__(self)` to enjoy event listeners and utilities. 

```python
class YourCoreLib(CoreLib):
  
  def __init__(self):
      CoreLib.__init__(self)
			...
```

