---
id: logger
title: Logging
sidebar: core_lib_doc_sidebar
permalink: logger.html
folder: core_lib_doc
toc: false
---

`@Logging` writes one log line **before** each call to the decorated function. The line comes from a message template filled in from the call's arguments, e.g. `'get_user_{user_id}'`. The logger name is the function's `__qualname__` (for a method, `ClassName.method_name`).

> **Optional utility.** You can use Core-Lib without it. It saves you the `logging.getLogger(...).log(...)` line at the top of a function, and fills the message from the arguments the same way `@Cache` builds its keys. It does **not** log return values or exceptions, and it does not configure logging: your application still calls `logging.basicConfig(...)` or sets up handlers.
>
> **Where it fits:** Service or DataAccess methods whose calls you want traced.

*core_lib.helpers.logging.Logging* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/logging.py#L7){:target="_blank"}

```python
class Logging(object):
    def __init__(self, message: str = '', level: int = logging.INFO):
```
**Arguments**

- **`message`** *`(str)`*: Message template to log. Use parameter names in braces, e.g. `'get_user_{user_id}'`, to include argument values. The template is filled by `build_function_key()` (see [Function Utilities](function_utils.html)), so a falsy argument (`0`, `''`, `None`) appears as `!E<name>E!`, and a name that is not a parameter appears as `!M<name>M!`. With no `message`, an empty line is logged.
- **`level`** *`(int)`*: Default `logging.INFO`. Accepts standard Python logging levels.


> **Warning:** log messages can expose sensitive data. For objects that may contain secrets, implement `Keyable.key()` and return only the safe fields.


**Example**

```python
import logging

from core_lib.helpers.func_utils import Keyable
from core_lib.helpers.logging import Logging

logging.basicConfig(level=logging.DEBUG)


class CustomerCreds(Keyable):
    def __init__(self, user_name: str, password: str):
        self.user_name = user_name
        self.password = password

    def key(self) -> str:
        return f'CustomerCreds(user_name:{self.user_name})'  # never the password


class Customer:
    @Logging(message='get_data_{customer_id}', level=logging.DEBUG)
    def get_data(self, customer_id: int):
        return {'id': customer_id}

    @Logging(message='login_{customer_creds}', level=logging.INFO)
    def login(self, customer_creds: CustomerCreds):
        return True


customer = Customer()
customer.get_data(5)                                # DEBUG:Customer.get_data:get_data_5
customer.login(CustomerCreds('jon_doe', 'secret'))  # INFO:Customer.login:login_CustomerCreds(user_name:jon_doe)
customer.get_data(0)                                # DEBUG:Customer.get_data:get_data_!Ecustomer_idE!
```

The comments show what `logging.basicConfig(level=logging.DEBUG)` prints. Without that line, Python's default setup shows only `WARNING` and above, so none of these lines would print.

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="instantiate_config.html">Previous</a></button>
    <button class="pageNext-btn"><a href="strings.html">Next</a></button>
</div>
