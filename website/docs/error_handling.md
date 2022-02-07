---
id: error_handler
title: Error Handlers
sidebar_label: Error Handlers
---

## Error Handlers
`Core-Lib` error handlers contain decorator and function which can raise exceptions for various scenarios.


### NotFoundErrorHandler Decorator
`NotFoundErrorHandler` decorator will raise `StatusCodeException` when the decorated function is not returning anything.

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

with StatusCodeAssert(status_code=500, message="some error occurred"):
    assert True == False # will raise an AssertionError
```

