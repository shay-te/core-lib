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

>**Warning** If you wish to log data, keep in mind that there's a potential that the data might include sensitive information, so proceed with caution.


##Usage

```python
import logging
from core_lib.helpers.logging import Logging

class Customer:
    @Logging(message="get_data_{id} logs", level=logging.DEBUG)
    def get_data(self, id):
        ...
        return data
    
    get_data(5) # will log ["DEBUG:Customer.get_data:get_data_5 logs"]
```