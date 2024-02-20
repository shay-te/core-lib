---
id: main
title: Getting started
sidebar: core_lib_doc_sidebar
permalink: index.html
folder: core_lib_doc
toc: false
---

# Why Core-Lib?
There are a variety of tools and frameworks available to you when building a web application. However, we believe Core-Lib is the best choice for building modern, full-stack web applications.

<b>`Core-Lib` was born to make the day-to-day work, The `"work itself."` easy to master.</b>

### Componentization
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Core-Lib facilitates modular development by breaking down functionalities into smaller, manageable components. This componentization enhances code organization and makes it easier to understand and maintain code.

### Reusability
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Core-Lib helps developers reuse components within the core-lib across different modules, reducing redundancy and saving development time. This reusability fosters consistency and standardization across projects.

### Ease of Test & Debug
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The componentized structure of the core-lib enables developers to test individual components in isolation, allowing for more targeted and effective testing. This leads to higher code quality and fewer bugs in the final product.

### Scalability
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;As the project grows, the core-lib scales with it. Small core-libs can be created for microservices and called inside a main core-lib. New core-libs (features) can be added without significantly impacting existing functionalities, making it easier to maintain and extend the project over time.

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
#### `your_core_lib.yaml` Explained:
<b>your_core_lib.yaml is the setting for your entire Core-Lib library. The above example will show how to configure core-lib to connect to a database using [SQLAlchemy](https://docs.sqlalchemy.org/en/20/):</b>
- <b>log_queries:</b>False, meaning that SQL queries won't be logged. True, [echo flag](https://docs.sqlalchemy.org/en/20/core/engines.html#more-on-the-echo-flag) is set to true.
- <b>create_db:</b> Create all tables stored in this project-defined entities metadata.[1](https://docs.sqlalchemy.org/en/20/core/metadata.html#sqlalchemy.schema.MetaData.create_all)
- <b>session:</b> Configuration options related to SQLAlchemy sessions, which represent a "workspace" for interacting with the database.
- <b>pool_recycle:</b> Specifies the number of seconds after which a connection will be recycled. In this case, connections will be recycled every 3600 seconds (1 hour).
- <b>pool_pre_ping:</b> Control whether SQLAlchemy will "ping" the database before giving a connection from the pool to check if it's still valid. It's set to false, meaning that pre-pinging is disabled.
- <b>url:</b> Define the database connection URL. It might be a single URL or a URL structure defined.
```
data:
  sqlalchemy:
    log_queries: false
    url:
      protocol: postgresql
      username: ${oc.env:POSTGRES_USER}
      password: ${oc.env:POSTGRES_PASSWORD}
      host: ${oc.env:POSTGRES_HOST}
      port: ${oc.env:POSTGRES_PORT}
      file: ${oc.env:POSTGRES_DB}
```
  - <b>protocol:</b> Specifies the protocol used for the database connection. In this case, it's set to sqlite, indicating the usage of SQLite as the database backend.

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
#### `your_core_lib.yaml` Explained:
<b>Python script or application that uses a custom CoreLib class and a SqlAlchemyConnectionRegistry class to manage database connections.</b>
- <b>Importing necessary modules:</b>
CoreLib from core_lib.core_lib
SqlAlchemyConnectionRegistry from core_lib.connection.sql_alchemy_connection_registry
#### Defining a new class YourCoreLib that inherits from CoreLib.
  - Defining an __init__ method for YourCoreLib that takes a config argument of type DictConfig. [DictConfig](https://omegaconf.readthedocs.io/en/2.3_branch/api_reference.html#id1) is a dictionary type from omegaconf that used by Hydra.
  - Calling the parent class CoreLib's __init__ method using CoreLib.__init__(self) to initialize the base class.
    - Mark core-lib started
    - Enable use of CoreLibListeners
    - Enable use of core-lib observers
  - Creating a db_connection object by initializing an instance of SqlAlchemyConnectionRegistry with the SQLAlchemy configuration provided in self.config.core_lib.data.sqlalchemy (In Python, self is a reference to the current instance of a class). 
  - This suggests that SqlAlchemyConnectionRegistry is responsible for managing SQLAlchemy database connections based on the provided configuration.
  - Initializing a UserDataAccess object, presumably a class responsible for accessing user data from the database, passing the db_connection object to it.


### From Main

```python
@hydra.main(config_path='.', config_name='core_lib_config.yaml')
def main(cfg):
	your_core_lib = YourCoreLib(cfg)
  ...

if __name__ == '__main__':
	main()
```
#### `From Main` Explained:
<b>Using the [Hydra](https://hydra.cc/docs/intro/) library to manage configuration for your script.</b>

#### Decorator: @hydra.main:
- This decorator tells Hydra to use the specified YAML configuration file (core_lib_config.yaml) located in the current directory ('.') to configure your application. It's a convenient way to manage configurations for your script.
- def main(cfg): This is the main function of your script, which takes a cfg argument. This argument will hold the configuration provided by Hydra.
#### Inside the main function:
  - <b>your_core_lib = YourCoreLib(cfg):</b> This line initializes an instance of the YourCoreLib class (defined earlier) using the configuration cfg provided by Hydra. This means that your application will use the configuration parameters specified in core_lib_config.yaml to set up the YourCoreLib instance.
  - <b>...:</b> This ellipsis (...) represents the rest of your main function, where you would perform other actions or operations specific to your application.
  - <b>`if __name__ == '__main__':`:</b> This conditional statement checks if the script is being executed directly (as opposed to being imported as a module). It ensures that the main function is only called when the script is run directly.
  - <b>main():</b> This line calls the main function when the script is executed directly, starting the execution of your application.

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
#### Code Explained:
<b>Writing unit tests for your YourCoreLib class using the unittest framework, alongside Hydra for configuration management.</b>
- <b>Importing necessary modules:</b>

  - <b>unittest:</b> Standard Python module for writing unit tests.
  - <b>hydra:</b> Hydra library for managing configurations.
  - <b>GlobalHydra:</b> A class from Hydra used for global configuration management.
- <b>Defining a function `get_config()` to use Hydra for loading testing `config.yaml` located under the testing folder.</b>
  - Clearing any existing Hydra configuration.
  - Initializing Hydra with a configuration path pointing to `../data/config and using config.yaml`.
  - Composing configuration, presumably loading it into memory, and returning it.
  - Creating an instance of YourCoreLib using the configuration obtained from get_config().
  - Processing outside the test case class, ensuring the configuration is set up before running any tests.

- <b>Defining a test case class TestCrud that inherits from unittest.TestCase.</b>

  - <b>Implementing the setUp method:</b>
    - Called before each test method is executed.
    - Initializes an instance of YourCoreLib using the configuration obtained earlier and assigns it to self.your_core_lib.
- <b>Defining the test method test_your_core_lib:</b>

  - This method tests functionality related to creating and retrieving a user.
  - It creates a user using self.your_core_lib.user.create() method, passing in a dictionary with user data.
  - Then, it retrieves the user using self.your_core_lib.user.get() method with the user's ID obtained from the creation step.
  - Finally, it asserts that the retrieved user matches the created user.

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
#### Code Explained:
<b>Implementing a singleton pattern for your YourCoreLib class using a separate class YourCoreLibInstance.</b>
- <b>init(core_lib_cfg):</b>

  - This is a static method (decorated with @staticmethod) responsible for initializing the singleton instance of YourCoreLib.
  - It takes a core_lib_cfg argument, presumably a configuration needed to initialize YourCoreLib.
  - If _app_instance is not already set (i.e., it's None), it initializes _app_instance by creating an instance of YourCoreLib with the provided configuration.
- <b>get() -> YourCoreLib:</b>
  - This is another static method responsible for returning the singleton instance of YourCoreLib.
  - It simply returns the _app_instance, which is the singleton instance of YourCoreLib.

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
#### Code Explained:
<b>Defining API endpoints using Flask (or a similar framework) to handle requests related to updating a user. </b>
- <b>Importing necessary functions from core_lib.web_helpers.request_response_helpers:</b>
  - request_body_dict: A function that extracts and parses the request body into a dictionary.
  - response_ok: A function that generates a successful response with an appropriate status code.
  - response_status: A function that generates a response with a specified HTTP status code.
  - Getting the singleton instance of YourCoreLib using YourCoreLibInstance.get(). This ensures that you're using the same instance of YourCoreLib throughout your application.

- <b>Defining two API endpoint functions: api_update_user.</b>
  - <b><i>api_update_user (for POST requests):</i></b>
    - <i>Decorated with @require_POST:</i> This decorator ensures that the endpoint only responds to POST requests.
    - <i>Decorated with @RequireLogin():</i> This decorator ensures that the user must be logged in to access this endpoint.
    - <i>Decorated with @HandleException():</i> This decorator handles any exceptions that occur within the endpoint function.
    - Inside the function, your_core_lib.user.update() is called to update the user information using the data from the request body (request_body_dict(request)).
    - Finally, it returns a response with HTTP status code NO_CONTENT using response_status(HTTPStatus.NO_CONTENT).
  - <b><i>api_update_user (for GET requests):</i></b>
    - <i>Decorated with @require_GET:</i> This decorator ensures that the endpoint only responds to GET requests.
    - <i>Decorated with @RequireLogin():</i> This decorator ensures that the user must be logged in to access this endpoint.
    - <i>Decorated with @HandleException():</i> This decorator handles any exceptions that occur within the endpoint function.
    - Inside the function, your_core_lib.user.update() is called to update the user information using the data from the request body (request_body_dict(request)).
    - Finally, it returns a successful response using response_ok().

## Installing

    pip install core-lib

## Requirements

    python > 3.7

## Running tests

    python -m unittest discover

- <b>python -m unittest:</b> This invokes Python's built-in unittest module as a script. The -m flag tells Python to run a module as a script, and unittest is the module we're running.
- <b>discover:</b> This is a command provided by the unittest module for automatically discovering and running tests. When you run discover, Python searches for all test modules (files starting with test_ or ending with _test.py) within the current directory and its subdirectories, loads them, and runs all test cases they contain.

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

