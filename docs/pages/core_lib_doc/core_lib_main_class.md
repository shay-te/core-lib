---
id: core_lib_main_class
title: Core Lib Class
sidebar: core_lib_doc_sidebar
permalink: core_lib_main_class.html
folder: core_lib_doc
toc: false
---

*core_lib.core_lib.CoreLib* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/core_lib.py#L17)

`CoreLib` class is the front of the entire library. It exposes all the "Services" your library offers by using simple `Services`, `DataAccess`, and `Clients` assignments to YourCoreLib class. You define your library interface. 



## Usage 
```python
from core_lib.core_lib import CoreLib
from core_lib.helpers.config_instances import instantiate_config
...

class YourCoreLib(CoreLib):
    def __init__(self, config: DictConfig):
        CoreLib.__init__(self)
        self.email = instantiate_config(self.config, EmailCoreLib)  # instantiate `EmailCoreLib` from config
        user_da = UserDataAccess(instantiate_config(self.config.core_lib.data.db, SqlAlchemyConnectionRegistry)) 
        self.user = UserService(user_da)
        self.user_photos = UserPhotosService(user_da)        
        ...
```
#### Code Explained:
- `YourCoreLib` class is extending CoreLib class
- __init__ method:
  - services are being instantiated, such as EmailCoreLib, UserDataAccess, UserService, and UserPhotosService.
- <b>self.email:</b> An instance of EmailCoreLib is instantiated using instantiate_config function, passing self.config as a parameter.
- <b>user_da:</b> An instance of UserDataAccess is created, utilizing SqlAlchemyConnectionRegistry instantiated from self.config.core_lib.data.db.
- <b>self.user:</b> An instance of UserService is created, passing user_da as a parameter.
- <b>self.user_photos:</b> An instance of UserPhotosService is created, also passing user_da as a parameter.


## init()

*core_lib.core_lib.CoreLib.\_\_init\_\_()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/core_lib.py#L22)

When extending  `CoreLib` class call  `CoreLib.__init__(self)` to initilize event listeners and set the `core_lib_started` flag to `False` . 

```python
class YourCoreLib(CoreLib):
  
  def __init__(self):
      CoreLib.__init__(self)
			...
```
#### Code Explained:
- __init__ method of the parent class CoreLib using CoreLib.__init__(self)
