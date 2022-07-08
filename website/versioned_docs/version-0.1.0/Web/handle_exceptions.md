---
id: handle_exceptions
title: HandleException Decorator
sidebar_label: handle_exception Decorator
---

## HandleException Decorator

*core_lib.web_helpers.decorators.HandleException* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/decorators.py#L34)

`Core-Lib`'s `web_helpers` provides `HandleException` decorator, that logs the exception, and it's error message and returns a `Http Response Object` 
with error message and appropriate status code.

```python
class HandleException(object):
```
>Can be configured with `Flask` and `Django` with the help of `Core-Lib`'s `WebHelpersUtils`.

Can handle exceptions for:
- `StatusCodeException` a part of `Core-Lib`'s `error_handling` class, raises a `StatusCodeException` with the given `status_code` if the user wants to return a different status code.
- `AssertionError` returns a response with `Status Code 500` when an assertion fails.
- `BaseException` returns a response with `Status Code 500` when any other exceptions are raised.
- `ExpiredSignatureError` returns a response with `Status Code 401` while attempting to decode a jwt expired token using the `JWTTokenHandler`.


**Example**

```python
from http import HTTPStatus

from core_lib.web_helpers.decorators import HandleException
from core_lib.error_handling.status_code_exception import StatusCodeException
from core_lib.web_helpers.request_response_helpers import response_json

@HandleException
def get_user(request):
    # if this query fails decorator will log the entire Exception message and return HTTP Response with status code 500
    return response_json(example_core_lib.user.get(request.user.user_id))

get_user()# get the HTTP response as per the execution of query.

user_status = 'inactive'
@HandleException
def check_active(user_id):
    # decorator will log the AssertionError message and return HTTP Response with status code 500
    assert user_status == 'active'

@HandleException
def validate_user(user_id):
    ...
    if not user_validate:
        # decorator will log the StatusCodeException message and return HTTP response with status_code 401 for unauthorized
        raise StatusCodeException(HTTPStatus.UNAUTHORIZED)
```

## handle_exception Function

*core_lib.web_helpers.decorators.handle_exception()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/web_helpers/decorators.py#L13)

`handle_exception` function is also being used by the `HandleException` decorator, this function is responsible for
returning HTTP response for the raised exception.

```python
def handle_exception(func, *args, **kwargs):
```
**Arguments**

- **`func`**: The function on which we need to handle exceptions.  
- __`*args, **kwargs`__: The args and kwargs of the function.

**Example**
```python
from http import HTTPStatus

from core_lib.web_helpers.decorators import handle_exception
from core_lib.error_handling.status_code_exception import StatusCodeException
from core_lib.web_helpers.request_response_helpers import response_json

def get_user(request):
    # if this query fails function will log the entire Exception message and return HTTP Response with status code 500
    return response_json(example_core_lib.user.get(request.user.user_id))

handle_exception(get_user())# get the HTTP response as per the execution of query.

user_status = 'inactive'
def check_active(user_id):
    assert user_status == 'active'

handle_exception(check_active(1)) # function will log the AssertionError message and return HTTP Response with status code 500

def validate_user(user_id):
    ...
    if not user_validate:
        raise StatusCodeException(HTTPStatus.UNAUTHORIZED)

handle_exception(validate_user(1))# function will log the StatusCodeException message and return HTTP response with status_code 401 for unauthorized
```

