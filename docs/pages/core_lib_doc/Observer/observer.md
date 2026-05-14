---
id: observer
title: Observer
sidebar: core_lib_doc_sidebar
permalink: observer.html
folder: core_lib_doc
toc: false
---

Services often need to react to events in other services — a user update triggers a cache clear, a payment triggers an email — but you don't want services importing each other. The Observer pattern solves this: one service emits a named event, listeners react to it, and neither knows the other exists.

> **Where it fits:** Cross-cutting glue. Observer sits *alongside* the six layers from the [home page](/index.html#the-layers), not as a layer of its own.

---

## ObserverListener

*core_lib.observer.observer_listener.ObserverListener* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/observer/observer_listener.py#L4){:target="_blank"}

Subclass `ObserverListener` and implement `update(key, value)` to react to events. The `key` identifies which event fired; `value` carries event data. Define your event keys as constants on the listener so emitters can reference them by name.

```python
from core_lib.observer.observer_listener import ObserverListener


class UserObserverListener(ObserverListener):
    EVENT_USER_CHANGE = "EVENT_USER_CHANGE"

    def update(self, key: str, value):
        if key == UserObserverListener.EVENT_USER_CHANGE:
            # invalidate cache, send notification, etc.
            ...
```

## Setting up the observer

Register an `Observer` (with its listeners attached) in your `CoreLib.__init__`. The `ObserverRegistry` is shared across `CoreLib`, so the `@Observe` decorator can find it.

```python
from omegaconf import DictConfig
from core_lib.core_lib import CoreLib
from core_lib.observer.observer import Observer


class MyCoreLib(CoreLib):
    def __init__(self, conf: DictConfig):
        super().__init__()
        self.config = conf

        main_observer = Observer()
        main_observer.attach(UserObserverListener())
        CoreLib.observer_registry.register("main", main_observer)
```

## `@Observe` decorator

*core_lib.observer.observer_decorator.Observe* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/observer/observer_decorator.py#L7){:target="_blank"}

Decorate any method to fire an event before or after it runs. Listeners attached to the matching `Observer` receive `update(key, value)`.

```python
class Observe(object):
    def __init__(
        self,
        event_key: str,
        value_param_name: str = None,
        observer_name: str = None,
        notify_before: bool = False,
    ):
```

**Arguments**

- **`event_key`** *`(str)`*: The event key listeners will see in `update()`.
- **`value_param_name`** *`(str)`*: Default `None`. The name of a parameter whose value should be passed as `value`. If unset, the full kwargs dict is passed.
- **`observer_name`** *`(str)`*: Default `None`. Which observer in `ObserverRegistry` to notify (when you have multiple).
- **`notify_before`** *`(bool)`*: Default `False`. When `True`, listeners are notified before the decorated function runs; when `False`, after.

**Example**

```python
class UserDataAccess(DataAccess):
    def __init__(self, db: SqlAlchemyConnectionFactory):
        self._db = db

    @Observe(event_key=UserObserverListener.EVENT_USER_CHANGE)
    def update(self, user_id: int, update):
        with self._db.get() as session:
            session.query(User).filter(User.id == user_id).update(update)
```

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/test_core_lib.html">Previous</a></button>
    <button class="pageNext-btn"><a href="/core_lib_listener.html">Next</a></button>
</div>
