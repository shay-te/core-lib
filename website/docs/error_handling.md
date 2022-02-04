---
id: error_handler
title: Error Handlers
sidebar_label: Error Handlers
---

## Error Handlers
Core-Lib error handlers contain decorator and function which can raise Exceptions for various scenarios.


### NotFoundErrorHandler Decorator
Using the `NotFoundErrorHandler` decorator for raising a `StatusCodeException` which will raise an exception when a desired value is not being returned ar passed to a function.

```python
class NotFoundErrorHandler(object):

    def __init__(self, message: str = None):
        self.message = message

    def __call__(self, func, *args, **kwargs):

        @wraps(func)
        def _wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if not result:
                logger.debug("NotFoundErrorHandler for function `{}`.".format(func.__qualname__))
                exception_message = build_value_by_func_parameters(self.message, func, *args, **kwargs) if self.message else None
                raise StatusCodeException(HTTPStatus.NOT_FOUND.value, exception_message)
            return result

        return _wrapper
```

#### Usage
 ```python
from core_lib.error_handling.not_found_decorator import NotFoundErrorHandler

@NotFoundErrorHandler()
def foo(param):
    return param

foo() # will raise a StatusCodeException for parameter NOT_FOUND
```

### StatusCodeAssert Function
`StatusCodeAssert` will check if an assertion passes and if not, then will throw an `AssertionError`

#### Usage
 ```python
from core_lib.error_handling.status_code_assert import StatusCodeAssert

with StatusCodeAssert(status_code=500, message="some error occurred"):
    assert True == False # will raise an AssertionError
```

