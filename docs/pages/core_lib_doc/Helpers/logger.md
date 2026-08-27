---
id: logger
title: Logging
sidebar: core_lib_doc_sidebar
permalink: logger.html
folder: core_lib_doc
toc: false
---

Adding a log line to every service method is tedious and easy to forget. The `@Logging` decorator instruments any function automatically — logging call arguments and return values — without touching the function body.

> **Where it fits:** Service or DataAccess helper. Apply `@Logging` to any method whose calls you want traced.

*core_lib.helpers.logging.Logging* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/logging.py#L7){:target="_blank"}

```python
class Logging(object):
    def __init__(self, message: str = '', level: int = logging.INFO):
```
**Arguments**

- **`message`** *`(str)`*: Message template to log. Use parameter names in braces, e.g. `'get_user_{user_id}'`, to include argument values.
- **`level`** *`(int)`*: Default `logging.INFO`. Accepts standard Python logging levels.


> **Warning:** log messages can expose sensitive data. For objects that may contain secrets, implement `Keyable.key()` and return only the safe fields.


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

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/instantiate_config.html">Previous</a></button>
    <button class="pageNext-btn"><a href="/strings.html">Next</a></button>
</div>
