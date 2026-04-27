---
id: middleware
title: Middleware
sidebar: core_lib_doc_sidebar
permalink: middleware.html
folder: core_lib_doc
toc: false
---

When you need to run the same logic before or after every operation — logging, auditing, validation, rate limiting — middleware lets you do it in one place rather than repeating it across every data access or service method.

Core-Lib's middleware system is a simple pipeline: add `Middleware` implementations to a `MiddlewareChain`, then call `execute(context)` to run them all in order.

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

chain.execute({'user_id': 42, 'action': 'update'})
```

## Wiring in your CoreLib

```python
from omegaconf import DictConfig
from core_lib.core_lib import CoreLib
from core_lib.middleware.middleware_chain import MiddlewareChain


class YourCoreLib(CoreLib):
    def __init__(self, config: DictConfig):
        super().__init__()
        self.config = config

        self.request_middleware = MiddlewareChain()
        self.request_middleware.add(LoggingMiddleware())
        self.request_middleware.add(ValidationMiddleware())
```

Then in your service or data access:

```python
class UserService(Service):
    def __init__(self, core_lib: YourCoreLib, data_access: UserDataAccess):
        self.middleware = core_lib.request_middleware
        self.data_access = data_access

    def update(self, context: dict):
        self.middleware.execute(context)
        return self.data_access.update(context['user_id'], context['data'])
```

---

# Middleware

*core_lib.middleware.middleware.Middleware* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/middleware/middleware.py){:target="_blank"}

Abstract base class. Implement `handle()` to define what this middleware does.

```python
class Middleware(ABC):
    @abstractmethod
    def handle(self, context: Any) -> None:
```

**Arguments**

- **`context`** *`(Any)`*: Shared data passed through the chain. Can be any object — a dict, a dataclass, a request wrapper. All middleware in the chain receive and can mutate the same context.

---

# MiddlewareChain

*core_lib.middleware.middleware_chain.MiddlewareChain* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/middleware/middleware_chain.py){:target="_blank"}

Holds an ordered list of `Middleware` instances and runs them sequentially.

```python
class MiddlewareChain:
    def __init__(self):
```

## Functions

### add()

*core_lib.middleware.middleware_chain.MiddlewareChain.add()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/middleware/middleware_chain.py){:target="_blank"}

Appends a middleware to the end of the chain.

```python
def add(self, middleware: Middleware):
```

**Arguments**

- **`middleware`** *`(Middleware)`*: The middleware instance to add.

### remove()

*core_lib.middleware.middleware_chain.MiddlewareChain.remove()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/middleware/middleware_chain.py){:target="_blank"}

Removes a previously added middleware. No-op if the middleware is not in the chain.

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

Runs `handle(context)` on each middleware in order. If any middleware raises an exception, execution stops and the exception propagates.

```python
def execute(self, context: Any):
```

**Arguments**

- **`context`** *`(Any)`*: The context object passed to every middleware in the chain.

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/job.html"><< Previous</a></button>
    <button class="pageNext-btn"><a href="/connection.html">Next >></a></button>
</div>
