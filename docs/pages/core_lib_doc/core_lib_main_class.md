---
id: core_lib_main_class
title: The CoreLib Class
sidebar: core_lib_doc_sidebar
permalink: core_lib_main_class.html
folder: core_lib_doc
toc: false
---

*core_lib.core_lib.CoreLib* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/core_lib.py#L17){:target="_blank"}

`CoreLib` is the entry point of your application. It is where you wire together services, data access, clients, and other dependencies. Everything else — web frameworks, jobs, scripts, and tests — calls into this class.

Think of `CoreLib` as the place where your application lives, and everything else plugs into it from the outside.

---

## Usage

```python
from core_lib.core_lib import CoreLib
from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.helpers.config_instances import instantiate_config
from omegaconf import DictConfig

class YourCoreLib(CoreLib):
    def __init__(self, config: DictConfig):
        super().__init__()

        db = SqlAlchemyConnectionFactory(config.core_lib.your_core_lib.data.db)  # connection at the edge
        user_da = UserDataAccess(db)

        self.user = UserService(user_da)          # business logic
        self.user_photos = UserPhotosService(user_da)

        self.email = instantiate_config(config, EmailCoreLib)  # child CoreLib via config
```

---

## How to think about it

`CoreLib` is not your business logic — it wires your business logic together.

- It is the only place where infrastructure (DB connections, caches, HTTP clients) is created
- Services receive their dependencies from `CoreLib.__init__`, not from imports
- The same instance runs behind web APIs, background jobs, scripts, and tests

Your services should never create their own connections — they should receive them.

---

## `__init__()`

*core_lib.core_lib.CoreLib.\_\_init\_\_()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/core_lib.py#L22){:target="_blank"}

When extending `CoreLib`, always call `super().__init__()` first. This initializes internal lifecycle hooks — event observers and the startup flag — that the framework depends on.

```python
class YourCoreLib(CoreLib):
    def __init__(self, config: DictConfig):
        super().__init__()
        ...
```

---

## Key idea

All dependencies are created in `__init__` — and nowhere else.

That is what keeps your services independent from frameworks, your code testable without external services, and your architecture from drifting over time.

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/project_structure.html"><< Previous</a></button>
    <button class="pageNext-btn"><a href="/registry.html">Next >></a></button>
</div>
