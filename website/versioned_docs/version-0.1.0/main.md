---
id: main
title: Getting started
sidebar_label: Getting started
---
#

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



## Usage	

```python
from core_lib.core_lib import CoreLib
from core_lib.helpers.config_instances import instantiate_config
...

class ExampleCoreLib(CoreLib):
    def __init__(self, config: DictConfig):
        CoreLib.__init__(self)
        self.email = instantiate_config(self.config, EmailCoreLib)
        user_da = UserDataAccess(instantiate_config(self.config.core_lib.data.db, SqlAlchemyConnectionRegistry))
        self.user = UserService(user_da)
        self.user_photos = UserPhotosService(user_da)  
```



#### From Main

```python
@hydra.main(config_path='.', config_name='core_lib_config.yaml')
def main(cfg):
	example_core_lib = ExampleCoreLib(cfg)
  ...

if __name__ == '__main__':
	main()
```



#### Unit-Test

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
    	self.example_core_lib = ExampleCoreLib(config)  
    
  def test_example_core_lib(self):
			user = self.example_core_lib.user.create({User.name.key: 'John Dow'})
      self.assertDictEqual(user, self.example_core_lib.user.get(user[User.id.key]))
```

#### Django

```python
from django.views.decorators.http import require_POST, require_GET
from http import HTTPStatus

class ExampleCoreLibInstance(object):
    _app_instance = None
    
		@staticmethod
    def init(core_lib_cfg):
        if not ExampleCoreLibInstance._app_instance:
          AppInstance._app_instance = ExampleCoreLib(core_lib_cfg)

    @staticmethod
    def get() -> ObjectiveLoveCoreLib:
        return ExampleCoreLibInstance._app_instance        

      
# view_user.py
example_core_lib = ExampleCoreLibInstance.get()

@require_POST
@RequireLogin()
@HandleException()
def api_update_user(request):
    example_core_lib.user.update(request.user.u_id, request_body_dict(request))
    return response_status(HTTPStatus.NO_CONTENT)

@require_GET
@RequireLogin()
@HandleException()
def api_update_user(request):
    objective_love_core_lib.user.update(request.user.u_id, request_body_dict(request))
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

