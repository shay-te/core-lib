---
id: middleware
title: Middleware
sidebar: core_lib_doc_sidebar
permalink: middleware.html
folder: core_lib_doc
toc: false
---

A `MiddlewareChain` is an ordered list of `Middleware` objects. Calling `chain.execute(context)` runs each one's `handle(context)` in turn.

Use it when several Service or DataAccess methods need the same check or side effect, such as logging, auditing, validation or rate limiting. Write each step once as a `Middleware` class, build the chain in your `CoreLib`, and call `chain.execute(context)` at the start of each method that needs it. Compared with calling helper functions directly, the steps are chosen in one place at startup, so adding or removing one does not mean editing every method.

It is a plain pipeline, not automatic interception. Nothing runs until you call `execute()`, and there is no "after" step. The one chain Core-Lib runs for you is `CoreLib.handle_exception_middleware`, on every exception caught by `@HandleException`; see [Exception Middleware Hook](handle_exceptions.html#exception-middleware-hook).

> **Where it fits:** Cross-cutting. A `MiddlewareChain` sits alongside the six layers; you call `chain.execute(context)` from inside a Service or DataAccess method to apply the same behavior before the real work runs.

*core_lib.middleware.middleware.Middleware* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/middleware/middleware.py){:target="_blank"}

*core_lib.middleware.middleware_chain.MiddlewareChain* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/middleware/middleware_chain.py){:target="_blank"}

## Usage

```python
from core_lib.middleware.middleware import Middleware
from core_lib.middleware.middleware_chain import MiddlewareChain


class LoggingMiddleware(Middleware):
    def handle(self, context) -> None:
        print(f'Processing: {context}')


class ValidationMiddleware(Middleware):
    def handle(self, context) -> None:
        if not context.get('user_id'):
            raise ValueError('user_id is required')


chain = MiddlewareChain()
chain.add(LoggingMiddleware())
chain.add(ValidationMiddleware())

chain.execute({'user_id': 42, 'action': 'update'})  # prints: Processing: {'user_id': 42, 'action': 'update'}
chain.execute({'action': 'update'})                 # prints, then raises ValueError: user_id is required
```

## Wiring in your CoreLib

Build the chain where you build everything else, in your `CoreLib`'s `__init__`, and pass it to the services that need it. `UserDataAccess` is the one from [The CoreLib Class](core_lib_main_class.html).

```python
from omegaconf import DictConfig

from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.core_lib import CoreLib
from core_lib.middleware.middleware_chain import MiddlewareChain

from your_core_lib.data_layers.data_access.user_data_access import UserDataAccess
from your_core_lib.data_layers.service.user_service import UserService
from your_core_lib.middlewares import LoggingMiddleware, ValidationMiddleware  # the classes from Usage


class YourCoreLib(CoreLib):
    def __init__(self, config: DictConfig):
        super().__init__()
        self.config = config

        db = SqlAlchemyConnectionFactory(config.core_lib.your_core_lib.data.db)

        request_middleware = MiddlewareChain()
        request_middleware.add(LoggingMiddleware())
        request_middleware.add(ValidationMiddleware())

        self.user = UserService(request_middleware, UserDataAccess(db))
```

The service runs the chain before doing the work:

```python
from core_lib.data_layers.service.service import Service
from core_lib.middleware.middleware_chain import MiddlewareChain

from your_core_lib.data_layers.data_access.user_data_access import UserDataAccess


class UserService(Service):
    def __init__(self, middleware: MiddlewareChain, user_da: UserDataAccess):
        self._middleware = middleware
        self._user_da = user_da

    def update(self, user_id: int, data: dict):
        self._middleware.execute({'user_id': user_id, 'action': 'update'})  # raises before the update if a check fails
        self._user_da.update(user_id, data)
```

---

## Middleware

*core_lib.middleware.middleware.Middleware* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/middleware/middleware.py){:target="_blank"}

Abstract base class. Implement `handle()` to define what this middleware does.

```python
class Middleware(ABC):
    @abstractmethod
    def handle(self, context: Any) -> None:
```

**Arguments**

- **`context`** *`(Any)`*: Shared data passed through the chain. Can be any object: a dict, a dataclass, a request wrapper. Every middleware in the chain receives the same object and can change it. The return value of `handle()` is ignored.

---

## MiddlewareChain

*core_lib.middleware.middleware_chain.MiddlewareChain* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/middleware/middleware_chain.py){:target="_blank"}

Holds an ordered list of `Middleware` instances and runs them in that order.

```python
class MiddlewareChain:
    def __init__(self):
```

## Functions

### add()

*core_lib.middleware.middleware_chain.MiddlewareChain.add()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/middleware/middleware_chain.py){:target="_blank"}

Appends a middleware to the end of the chain. Adding the same instance twice makes it run twice.

```python
def add(self, middleware: Middleware):
```

**Arguments**

- **`middleware`** *`(Middleware)`*: The middleware instance to add.

### remove()

*core_lib.middleware.middleware_chain.MiddlewareChain.remove()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/middleware/middleware_chain.py){:target="_blank"}

Removes a previously added middleware. Does nothing if the middleware is not in the chain.

```python
def remove(self, middleware: Middleware):
```

**Arguments**

- **`middleware`** *`(Middleware)`*: The middleware instance to remove.

### clear()

*core_lib.middleware.middleware_chain.MiddlewareChain.clear()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/middleware/middleware_chain.py){:target="_blank"}

Removes all middleware from the chain.

```python
def clear(self):
```

### execute()

*core_lib.middleware.middleware_chain.MiddlewareChain.execute()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/middleware/middleware_chain.py){:target="_blank"}

Runs `handle(context)` on each middleware in order. If one raises an exception, the ones after it do not run and the exception propagates to the caller of `execute()`.

```python
def execute(self, context: Any):
```

**Arguments**

- **`context`** *`(Any)`*: The context object passed to every middleware in the chain.

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="job.html">Previous</a></button>
    <button class="pageNext-btn"><a href="connection.html">Next</a></button>
</div>
