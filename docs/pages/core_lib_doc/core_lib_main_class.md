---
id: core_lib_main_class
title: The CoreLib Class
sidebar: core_lib_doc_sidebar
permalink: core_lib_main_class.html
folder: core_lib_doc
toc: false
---

*core_lib.core_lib.CoreLib* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/core_lib.py#L17){:target="_blank"}

`CoreLib` is the entry point of your application. It is where you wire services, data access, clients, and other dependencies together. Web frameworks, jobs, scripts, and tests all call into this class.

In the [Hello, World](/index.html#a-complete-core-lib-app-in-one-file) the entire `CoreLib` subclass was three lines. In a real project you typically load config from YAML and wire several services. The shape is the same.

---

## Usage in a real project

```python
from omegaconf import DictConfig
from core_lib.core_lib import CoreLib
from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory


class YourCoreLib(CoreLib):
    def __init__(self, config: DictConfig):
        super().__init__()

        # Connection at the edge — constructed once from config.
        db = SqlAlchemyConnectionFactory(config.core_lib.your_core_lib.data.db)

        # DataAccess wraps an entity and a Connection.
        user_da = UserDataAccess(db)

        # Services compose DataAccess (and Client) instances and expose business logic.
        self.user = UserService(user_da)
        self.user_photos = UserPhotosService(user_da)
```

A route handler, job, or test then just calls `your_core_lib.user.get(user_id)` — it never sees the database session.

---

## Rules

1. **All infrastructure is created in `__init__`.** Connections, clients, caches — nowhere else. Service code never imports a session, a Redis client, or an SDK.
2. **Always call `super().__init__()` first.** This initializes the internal lifecycle hooks (event observers and the startup flag) the framework depends on.
3. **Services receive their dependencies as constructor arguments.** No globals, no module-level state.

That is what keeps services independent from frameworks, code testable without external services, and architecture from drifting over time.

---

## `__init__()`

*core_lib.core_lib.CoreLib.\_\_init\_\_()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/core_lib.py#L22){:target="_blank"}

```python
class YourCoreLib(CoreLib):
    def __init__(self, config: DictConfig):
        super().__init__()
        ...
```

---

## Composing multiple `CoreLib`s

For larger systems you can nest a `CoreLib` inside another via Hydra's `_target_` — useful when a sub-system (e.g. an email module) is itself a self-contained Core-Lib that you want to drop in. See [Instantiate Config](/instantiate_config.html) for the pattern.

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/project_structure.html"><< Previous</a></button>
    <button class="pageNext-btn"><a href="/registry.html">Next >></a></button>
</div>
