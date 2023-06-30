---
id: main
title: Getting started
sidebar: core_lib_doc_sidebar
permalink: index.html
folder: core_lib_doc
toc: false
---

# Why Core-Lib?
`Core-Lib` was born to make the day-to-day work, The  `"work itself."` easy to master.

# What is Core-Lib?
`Core-Lib` is a framework for creating python applications as libraries. 

# How Core-Lib?
- `Core-Lib` is a plugin and plug-able to other `Core-Libs`. 
- `Core-Lib` can discover and merge other `Core-Lib` configurations. 
- `Core-Lib` provides basic/simple/loose tools. 
- `Core-Lib` is not delegating third-party libraries. 
- `Core-Lib` unit-test the entire library.
- `Core-Lib` deploys anywhere.
- `Core-Lib` recommends architecture and guidelines. 



## Example

`your_core_lib.yaml`

```yaml
# @package _global_
core_lib:
  ...
	data:
    sqlalchemy:
      log_queries: false
      create_db: true      
      session:
        pool_recycle: 3600
        pool_pre_ping: false      
      url:
        protocol: sqlite
  ...
```

`your_core_lib.py`

```python
from core_lib.core_lib import CoreLib
from core_lib.connection.sql_alchemy_connection_registry import SqlAlchemyConnectionRegistry

class YourCoreLib(CoreLib):
    def __init__(self, config: DictConfig):
        CoreLib.__init__(self)
        db_connection = SqlAlchemyConnectionRegistry(self.config.core_lib.data.sqlalchemy)
        self.user = UserDataAccess(db_connection)
        ...
```



### From Main

```python
@hydra.main(config_path='.', config_name='core_lib_config.yaml')
def main(cfg):
	your_core_lib = YourCoreLib(cfg)
  ...

if __name__ == '__main__':
	main()
```



### Unit-Test

```python
import unittest
import hydra
from hydra.core.global_hydra import GlobalHydra

def get_config():
  GlobalHydra.instance().clear()
  hydra.initialize(config_path=os.path.join('..', 'data', 'config'), caller_stack_depth=1)
  return hydra.compose('config.yaml')

config = get_config()

class TestCrud(unittest.TestCase):
	def setUp(self):
		self.your_core_lib = YourCoreLib(config)  
    
  def test_your_core_lib(self):
		user = self.your_core_lib.user.create({User.name.key: 'John Dow'})
    self.assertDictEqual(user, self.your_core_lib.user.get(user[User.id.key]))
```

### Django

##### your_core_lib_instance.py

```python
class YourCoreLibInstance(object):
    _app_instance = None
    
		@staticmethod
    def init(core_lib_cfg):
        if not YourCoreLibInstance._app_instance:
          YourCoreLibInstance._app_instance = YourCoreLib(core_lib_cfg)

    @staticmethod
    def get() -> YourCoreLib:
        return YourCoreLibInstance._app_instance        
```

##### view_user.py

```python
from core_lib.web_helpers.request_response_helpers import request_body_dict, response_ok, response_status

your_core_lib = YourCoreLibInstance.get()

@require_POST
@RequireLogin()
@HandleException()
def api_update_user(request):
    your_core_lib.user.update(request.user.u_id, request_body_dict(request))
    return response_status(HTTPStatus.NO_CONTENT)

@require_GET
@RequireLogin()
@HandleException()
def api_update_user(request):
    your_core_lib.user.update(request.user.u_id, request_body_dict(request))
    return response_ok()
```




## Installing

    pip install core-lib

## Requirements

    python > 3.7

## Running tests

    python -m unittest discover

## The source

[https://github.com/shay-te/core-lib](https://github.com/shay-te/core-lib)

## Example project

[https://github.com/shay-te/core-lib/examples](https://github.com/shay-te/core-lib/examples)

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct and the process for submitting pull requests to us.


## Authors

**Shay Tessler**  - [GitHub](https://github.com/shay-te)


## License

This project is licensed under the MIT - see the [LICENSE](https://github.com/shay-te/core-lib/blob/master/LICENSE) file for details.

