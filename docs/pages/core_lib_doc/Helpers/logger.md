---
id: logger
title: Logging
sidebar: core_lib_doc_sidebar
permalink: logger.html
folder: core_lib_doc
toc: false
---

# Logging

*core_lib.helpers.logging.Logging* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/logging.py#L7){:target="_blank"}

`Core-Lib`'s `Logging` decorator automatically logs function calls, it uses python's inbuilt `logging` to log function calls and the logs can also be customized in the logger.

```python
class Logging(object):
    def __init__(self, message: str = '', level: int = logging.INFO):
```
**Arguments**

- **`message`** *`(str)`*: The message to be logged, by supplying the parameter keys in the message string, this can additionally log the function's arguments.  
- **`level`** *`(int)`*: Default `logging.INFO` or int value `20`, accepts the logger level values as specified by the `logging` in python,
to know about the logger values [click here](https://docs.python.org/3/library/logging.html#logging-levels){:target="_blank"}.


>**Warning** If you wish to log data, keep in mind that there's a potential that the data might include sensitive information, we recommend to use `Keyable` class implementation.


**Example**

```python
import logging
from core_lib.helpers.logging import Logging
from core_lib.helpers.func_utils import Keyable

class CustomerCreds(Keyable):
    def __init__(self, c_name: str):
        self.c_name = c_name

    def key(self) -> str:
        return f'CustomerCreds(u_name:{self.c_name})'

class Customer:
    @Logging(message='get_data_{id} logs', level=logging.DEBUG)
    def get_data(self, id: int):
        ...
        return data
    
    @Logging(message='login_data_{customer_creds}', level=logging.ERROR)
    def login_data(self, customer_creds: CustomerCreds):
        ...
        return data
    

customer = Customer()
customer_id = 5
customer.get_data(customer_id) # logs ["DEBUG:Customer.get_data:get_data_5 logs"]
    
# For not logging sensitive data
customer.login_data(CustomerCreds('jon_doe')) # logs ['ERROR:Customer.login_data:login_data_CustomerCreds(u_name:jon_doe)']
```