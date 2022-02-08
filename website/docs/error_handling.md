---
id: error_handler
title: Error Handlers
sidebar_label: Error Handlers
---

## Error Handlers
`Core-Lib` error handlers contain decorator and function which can raise exceptions for various scenarios.

###StatusCodeException
Will raise an exception for the given `Status Code` ( to be passed as arguments ).

```python
class StatusCodeException(Exception):
    def __init__(self, status_code: int, *args, **kwargs):
        self.status_code = status_code
        super(StatusCodeException, self).__init__(*args, **kwargs)
```
`status_code`: Status code error to be raised.

`*args`, `**kwargs`: the extracted args and kwargs given to the class.

### NotFoundErrorHandler Decorator
`NotFoundErrorHandler` decorator will raise `StatusCodeException` when the decorated function is not returning anything.
For e.g., if a function is returning an empty `string ""`, `tuple ()`, `list []`, `dict {}` or `set()` `StatusCodeException` will be raised

#### Usage
 ```python
from core_lib.error_handling.not_found_decorator import NotFoundErrorHandler

@NotFoundErrorHandler()
def raise_expection():
    pass

raise_expection() # will raise a StatusCodeException for parameter NOT_FOUND
```

### StatusCodeAssert Function
Using `StatusCodeAssert` along with the `with` statement will capture any `AssertionError` and raise `StatusCodeException` with the status and message relevant to the application needs.

#### Usage
 ```python
from core_lib.error_handling.status_code_assert import StatusCodeAssert

user_status = 'inactive'
with StatusCodeAssert(status_code=500, message="some error occurred"):
    assert user_status == 'active' # will raise an AssertionError because the status is inactive.
```

