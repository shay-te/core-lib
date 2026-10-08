---
id: error_handler
title: Error Handlers
sidebar: core_lib_doc_sidebar
permalink: error_handler.html
folder: core_lib_doc
toc: false
---

These are the exception types and decorators Core-Lib uses to report errors with an HTTP status:

- `StatusCodeException`: an exception that carries an HTTP status code.
- `@NotFoundErrorHandler`: raises a 404 `StatusCodeException` when a function returns nothing.
- `@DuplicateErrorHandler`: turns a database integrity error into a 409 `StatusCodeException`.
- `StatusCodeAssert`: turns a failed `assert` into a `StatusCodeException`.
- `CoreLibInitException`: raised when a `CoreLib` is started twice.

Use them so that a Service or DataAccess can say "not found" or "conflict" without knowing anything about HTTP responses. Put [`@HandleException`](handle_exceptions.html) on your route handlers and it turns any `StatusCodeException` into a response with that status. Without `@HandleException` (or your own `try/except`), these are ordinary Python exceptions.

> **Where it fits:** Cross-cutting. `StatusCodeException` can be raised from any layer. `@NotFoundErrorHandler` is already on `get()` of the CRUD DataAccess bases. `@DuplicateErrorHandler` goes on the Service method that creates rows. `@HandleException` goes on web routes.

## StatusCodeException

*core_lib.error_handling.status_code_exception.StatusCodeException* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/error_handling/status_code_exception.py){:target="_blank"}

An `Exception` with a `status_code` attribute, so a web handler can turn it into the right response.

Use it when:

- a service or data access method needs to reject a request
- the caller should receive a specific HTTP status
- you want the error to pass through Core-Lib's exception handlers consistently

```python
class StatusCodeException(Exception):
    def __init__(self, status_code: int, *args, **kwargs):
        self.status_code = status_code
        super(StatusCodeException, self).__init__(*args, **kwargs)
```

**Arguments**

- **`status_code`** *`(int)`*: The HTTP status. An `HTTPStatus` member or a plain int.
- __`*args, **kwargs`__: Passed to `Exception`, usually one message string.

**Example**

```python
from http import HTTPStatus

from core_lib.error_handling.status_code_exception import StatusCodeException

raise StatusCodeException(HTTPStatus.BAD_REQUEST, 'Input parameter is invalid')
```

Under `@HandleException`, the client gets status `400` with the body `{"message": "Bad Request"}`. The message `'Input parameter is invalid'` is logged, not sent to the client; see [What the client gets](handle_exceptions.html#what-the-client-gets).

## NotFoundErrorHandler Decorator

*core_lib.error_handling.not_found_decorator.NotFoundErrorHandler* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/error_handling/not_found_decorator.py){:target="_blank"}

Raises `StatusCodeException` with status `404` when the decorated function returns a falsy value: `None`, `""`, `()`, `[]`, `{}`, `set()`, `0` or `False`. Otherwise it returns the function's result unchanged.

```python
class NotFoundErrorHandler(object):
    def __init__(self, message: str = None):
```

**Arguments**

- **`message`** *`(str)`*: Default `None`. The exception's message, written as a template that is filled in from the decorated function's arguments by name: `'no user with id {user_id}'`. A placeholder whose argument is missing or falsy (`None`, `0`, `''`) comes out as a marker such as `!Euser_idE!` instead of its value.

> **Watch out:** the check is `not return_value`, not `return_value is None`. Only put this decorator on functions whose valid results are always truthy (for example, a fetched ORM row). On a function whose valid result might be `0`, `False` or `[]`, it turns legitimate empty results into 404s.

The `get()` method of `CRUDDataAccess` and the other CRUD bases already has this decorator; see [CRUD](crud.html).

**Example**

```python
from core_lib.error_handling.not_found_decorator import NotFoundErrorHandler

USERS = {1: 'ada@example.com'}


@NotFoundErrorHandler('no user with id {user_id}')
def find_user(user_id: int):
    return USERS.get(user_id)


find_user(1)   # 'ada@example.com'
find_user(99)  # raises StatusCodeException: status_code 404, message 'no user with id 99'
```

## DuplicateErrorHandler Decorator

*core_lib.error_handling.duplicate_error_decorator.DuplicateErrorHandler* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/error_handling/duplicate_error_decorator.py){:target="_blank"}

Catches a SQLAlchemy `IntegrityError` raised by the decorated function and raises `StatusCodeException` with status `409 CONFLICT` instead.

It catches every `sqlalchemy.exc.IntegrityError`, not only unique-constraint violations: a missing `NOT NULL` value, a broken foreign key or a failed `CHECK` also becomes a 409. Other exceptions pass through unchanged.

```python
class DuplicateErrorHandler(object):
    def __init__(self, message: str = None):
```

**Arguments**

- **`message`** *`(str)`*: Default `None`. A template filled in from the decorated function's arguments, as for `NotFoundErrorHandler`: `'User with email {email} already exists'`.

**Example**

Put it on the Service method that creates the row. `User` is an entity whose `email` column is `unique=True`, and `UserDataAccess` is a `CRUDDataAccess` for it.

```python
from core_lib.data_layers.service.service import Service
from core_lib.data_transform.result_to_dict import ResultToDict
from core_lib.error_handling.duplicate_error_decorator import DuplicateErrorHandler
from your_core_lib.data_layers.data.db.entities.user import User
from your_core_lib.data_layers.data_access.user_data_access import UserDataAccess


class UserService(Service):
    def __init__(self, user_data_access: UserDataAccess):
        self._user_data_access = user_data_access

    @ResultToDict()
    @DuplicateErrorHandler('User with email {email} already exists')
    def create(self, email: str) -> dict:
        return self._user_data_access.create({User.email.key: email})
```

The first `create('ada@example.com')` returns `{'id': 1, 'email': 'ada@example.com'}`. The second raises `StatusCodeException` with status `409` and the message `'User with email ada@example.com already exists'`.

## StatusCodeAssert

*core_lib.error_handling.status_code_assert.StatusCodeAssert* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/error_handling/status_code_assert.py){:target="_blank"}

A context manager. If an `assert` inside the `with` block fails, it raises `StatusCodeException` with the status and message you give it. Other exceptions pass through unchanged.

```python
def StatusCodeAssert(status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR, message: str = None):
```

**Arguments**

- **`status_code`** *`(int)`*: Default `500`.
- **`message`** *`(str)`*: Default `None`. The exception's message.

**Example**

```python
from http import HTTPStatus

from core_lib.error_handling.status_code_assert import StatusCodeAssert

user_status = 'inactive'
with StatusCodeAssert(status_code=HTTPStatus.FORBIDDEN, message='User must be active'):
    assert user_status == 'active'  # fails: raises StatusCodeException(403, 'User must be active')
```

> Python removes `assert` statements when it runs with `-O`. Then the check inside the block does not run at all. Use an `if` and raise `StatusCodeException` yourself for checks that must always run.

## CoreLibInitException

*core_lib.error_handling.core_lib_init_exception.CoreLibInitException* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/error_handling/core_lib_init_exception.py){:target="_blank"}

Raised by `CoreLib.start_core_lib()` when it is called a second time on the same instance, with the message `'CoreLib already initialized'`. Other startup failures, such as bad config or an unreachable database, raise their own exceptions.

```python
class CoreLibInitException(Exception):
    pass
```

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="client_base.html">Previous</a></button>
    <button class="pageNext-btn"><a href="data_transform_helpers.html">Next</a></button>
</div>
