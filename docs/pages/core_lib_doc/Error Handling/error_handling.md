---
id: error_handler
title: Error Handlers
sidebar: core_lib_doc_sidebar
permalink: error_handler.html
folder: core_lib_doc
toc: false
---

`Core-Lib` error handlers contain decorator and function which can raise exceptions for various scenarios.

## StatusCodeException

*core_lib.error_handling.status_code_exception.StatusCodeException* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/error_handling/status_code_exception.py#L1){:target="_blank"}

`StatusCodeException` is the primary and single exception used by any `Core-Lib`.

It serves three primary purposes:

- Unified way to handle errors while using `Core-Lib`.
- Reflect any error with a numeric status code.
- Bridge between library errors and HTTP Status code.

```python
class StatusCodeException(Exception):
    def __init__(self, status_code: int, *args, **kwargs):
        self.status_code = status_code
        super(StatusCodeException, self).__init__(*args, **kwargs)
```

**Arguments**

- **`status_code`** *`(int)`*: Status code error to be raised.
- __`*args, **kwargs`__: The extracted args and kwargs given to the class.

**Example**

```python
from http import HTTPStatus
from core_lib.error_handling.status_code_exception import StatusCodeException

raise StatusCodeException(HTTPStatus.BAD_REQUEST, 'Input parameter is invalid')
```



## NotFoundErrorHandler Decorator

*core_lib.error_handling.not_found_decorator.NotFoundErrorHandler* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/error_handling/not_found_decorator.py#L11){:target="_blank"}


`NotFoundErrorHandler` decorator will raise `StatusCodeException` when the decorated function is not returning anything.  
For e.g., if a function is returning an empty `string ""`, `tuple ()`, `list []`, `dict {}` `set()` or `None` `StatusCodeException` will be raised.

**Example**

 ```python
from core_lib.error_handling.not_found_decorator import NotFoundErrorHandler

@NotFoundErrorHandler()
def raise_expection():
    pass

raise_expection() # will raise a StatusCodeException for parameter NOT_FOUND
```



## StatusCodeAssert Function

*core_lib.error_handling.status_code_assert.StatusCodeAssert* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/error_handling/status_code_assert.py#L9){:target="_blank"}

Using `StatusCodeAssert` along with the `with` statement will capture any `AssertionError` and raise `StatusCodeException` with the status and message relevant to the application needs.

**Example**
 ```python
from core_lib.error_handling.status_code_assert import StatusCodeAssert

user_status = 'inactive'
with StatusCodeAssert(status_code=500, message="User must be active"):
    assert user_status == 'active' # will raise an AssertionError because the status is inactive.
```

## CoreLibInitException Function
*core_lib.error_handling.core_lib_init_exception.CoreLibInitException* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/error_handling/core_lib_init_exception.py){:target="_blank"}

`CoreLibInitException` decorator handles any exception raised while initialization of `core-lib`.

**Example**
 ```python
class CoreLibInitException(Exception):
    pass
```

## DuplicateErrorHandler Function
*core_lib.error_handling.duplicate_error_handler.DuplicateErrorHandler* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/error_handling/duplicate_error_decorator.py){:target="_blank"}

`DuplicateErrorHandler` decorator will raise `StatusCodeException` when the decorated function adds the same value in the column of the database table which accepts unique values only.

**Example**
 ```python
import logging
from functools import wraps
from http import HTTPStatus

from sqlalchemy import exc

from core_lib.error_handling.status_code_exception import StatusCodeException
from core_lib.helpers.func_utils import build_function_key

logger = logging.getLogger(__name__)


class DuplicateErrorHandler(object):
    def __init__(self, message: str = None):
        self.message = message

    def __call__(self, func, *args, **kwargs):
        @wraps(func)
        def _wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exc.IntegrityError as e:
                logger.debug(f'DuplicateErrorHandler for function `{func.__qualname__}`.')
                exception_message = build_function_key(self.message, func, *args, **kwargs) if self.message else None
                raise StatusCodeException(HTTPStatus.CONFLICT, exception_message)

        return _wrapper

```

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/client_base.html"><< Previous</a></button>
    <button class="pageNext-btn"><a href="/data_transform_helpers.html">Next >></a></button>
</div>