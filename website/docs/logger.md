---
id: logger
title: Logging
sidebar_label: Logging
---

# Logging
`Core-Lib`'s `Logging` decorator automatically logs function call, it uses python's inbuilt `logging` to log function calls and the logs can also be customized in the logger.

```python
class Logging(object):
    def __init__(self, message: str = '', level: int = logging.INFO):
```
`message` type `str`, the message to be logged, by supplying the parameter keys in the message string, this can additionally log the function's arguments.

`level` type `int`, default `logging.INFO` or int value `20`, accepts the logger level values as specified by the `logging` in python,
to know about the logger values [click here](https://docs.python.org/3/library/logging.html#logging-levels).

>**Warning** If you wish to log data, keep in mind that there's a potential that the data might include sensitive information, we recommend to use `Keyable` class implementation.


##Usage

```python
import logging
from core_lib.helpers.logging import Logging
from core_lib.helpers.func_utils import Keyable

class CustomerCreds(Keyable):
    def __init__(self, c_name, password):
        self.c_name = c_name
        self.password = password

    def key(self) -> str:
        return f'CustomerCreds(u_name:{self.c_name}, password:{type(self.password).__name__})'

class Customer:
    @Logging(message="get_data_{id} logs", level=logging.DEBUG)
    def get_data(self, id):
        ...
        return data
    
    @Logging(message="login_data_{customer_creds}", level=logging.ERROR)
    def login_data(self, customer_creds):
        ...
        return data
    
    
    get_data(5) # logs ["DEBUG:Customer.get_data:get_data_5 logs"]
    
    # For not logging sensitive data
    login_data(CustomerCreds('jon_doe', 'password@12345')) # logs ['ERROR:Customer.login_data:login_data_CustomerCreds(u_name:jon_doe, password:str)']
```