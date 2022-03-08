---
id: handle_exceptions
title: handle_exceptions Decorator
sidebar_label: handle_exceptions Decorator
---

## handle_exceptions Decorator
`Core-Lib`'s `web_helpers` provides `handle_exception` decorator, that logs the exception, and it's error message and returns a `Http Response Object` 
with error message in case of any exception. 

```python
def handle_exceptions(func):
```
>Can be configured with `Flask` and `Django` with the help of `Core-Lib`'s `WebHelpersUtils`.

Can handle exceptions for:
- `StatusCodeException` a part of `Core-Lib`'s `error_handling` class, raises a `StatusCodeException` with the given `status_code` if the user wants to return a different status code.
- `AssertionError` returns response with `Status Code 500` when an assertion fails.
- `BaseException` returns response with `Status Code 500` when any other exceptions are raised.

### Usage
```python
from http import HTTPStatus

from core_lib.web_helpers.decorators import handle_exceptions
from core_lib.error_handling.status_code_exception import StatusCodeException
from core_lib.web_helpers.request_response_helpers import response_json

@handle_exceptions
def get_user(request):
    # if this query fails decorator will log the entire Exception message and return HTTP Response with status code 500
    return response_json(example_core_lib.user.get(request.user.user_id))

get_user()# get the HTTP response as per the execution of query.

user_status = 'inactive'
@handle_exceptions
def check_active(self, user_id):
    # decorator will log the AssertionError message and return HTTP Response with status code 500
    assert user_status == 'active'

@handle_exceptions
def validate_user(self, user_id):
    ...
    if not user_validate:
        # decorator will log the StatusCodeException message and return HTTP response with status_code 401 for unauthorized
        raise StatusCodeException(HTTPStatus.UNAUTHORIZED)
```

