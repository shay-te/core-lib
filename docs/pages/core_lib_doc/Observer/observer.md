---
id: observer
title: Observer
sidebar: core_lib_doc_sidebar
permalink: observer.html
folder: core_lib_doc
toc: false
---

An `Observer` holds a list of listeners. A method decorated with `@Observe(event_key=...)` notifies those listeners every time it runs, passing the event key and a value.

Use it when one part of your code should react to something another part did (a user update clears a cache, a payment sends an email) without the emitting service calling the reacting code itself. The emitter only names an event key; which listeners react is decided once, where you set up the `Observer` in your `CoreLib`.

Listeners run synchronously, in the same call. They are not a queue or a background job, and an exception in a listener reaches the caller of the decorated method (see [When a listener fails](#when-a-listener-fails)).

> **Where it fits:** Cross-cutting glue. Observer sits *alongside* the six layers from the [home page](index.html#the-layers), not as a layer of its own.

---

## ObserverListener

*core_lib.observer.observer_listener.ObserverListener* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/observer/observer_listener.py){:target="_blank"}

Subclass `ObserverListener` and implement `update(key, value)` to react to events. `key` says which event fired; `value` carries the event data. Define your event keys as constants on the listener so emitters can reference them by name.

```python
from core_lib.observer.observer_listener import ObserverListener


class UserObserverListener(ObserverListener):
    EVENT_USER_CHANGE = 'EVENT_USER_CHANGE'

    def update(self, key: str, value):
        if key == UserObserverListener.EVENT_USER_CHANGE:
            print(f'user {value} changed')  # clear a cache, send a notification, ...
```

## Observer

*core_lib.observer.observer.Observer* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/observer/observer.py){:target="_blank"}

Holds the listeners for one group of events.

```python
class Observer(object):
    def __init__(self, listener: ObserverListener = None, listener_type: object = None):
```

- **`listener`**: Optional. A first listener to attach.
- **`listener_type`**: Optional. If set, `attach()` only accepts instances of this class.
- **`attach(listener)`** / **`detach(listener)`**: Add or remove a listener.
- **`notify(key, value)`**: Calls `update(key, value)` on each listener, in the order they were attached. `@Observe` calls this for you.

## Setting up the observer

Create the `Observer`, attach its listeners and register it on `CoreLib.observer_registry` in your `CoreLib.__init__`. `@Observe` finds it there by name.

`CoreLib.observer_registry` is a class attribute: one registry for the whole process, shared by every `CoreLib` instance. Registering a name that is already registered raises `ValueError`, so guard the registration as below. Without the guard, creating your `CoreLib` a second time in the same process fails. [`load_core_lib_config()`](test_core_lib.html#load_core_lib_config), used in tests, clears the registry each time it is called.

```python
# your_core_lib/constants.py
USER_OBSERVER = 'user'
```

```python
# your_core_lib/your_core_lib.py
from omegaconf import DictConfig

from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.core_lib import CoreLib
from core_lib.observer.observer import Observer

from your_core_lib.constants import USER_OBSERVER
from your_core_lib.data_layers.data_access.user_data_access import UserDataAccess
from your_core_lib.data_layers.service.user_service import UserService
from your_core_lib.user_observer_listener import UserObserverListener


class YourCoreLib(CoreLib):
    def __init__(self, config: DictConfig):
        super().__init__()
        self.config = config

        if not CoreLib.observer_registry.get(USER_OBSERVER):
            user_observer = Observer()
            user_observer.attach(UserObserverListener())
            CoreLib.observer_registry.register(USER_OBSERVER, user_observer)

        db = SqlAlchemyConnectionFactory(config.core_lib.your_core_lib.data.db)
        self.user = UserService(UserDataAccess(db))
```

## `@Observe` decorator

*core_lib.observer.observer_decorator.Observe* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/observer/observer_decorator.py){:target="_blank"}

Decorate a method to notify an observer's listeners each time the method runs: after it returns (the default) or before it starts. Listeners receive `update(event_key, value)`.

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

- **`event_key`** *`(str)`*: The key listeners receive in `update()`.
- **`value_param_name`** *`(str)`*: Default `None`. The name of one parameter of the decorated method; listeners receive that argument as `value`. The caller must pass that argument **positionally**: with `value_param_name='user_id'`, `update(1, data)` works, but `update(user_id=1, data=data)` raises `IndexError`. When `None`, `value` is a dict of all the call's arguments by parameter name, including `self` for methods and any default values. For the example below that is a dict with the keys `self`, `user_id` and `data`.
- **`observer_name`** *`(str)`*: Default `None`. The name the observer was registered under. When `None`, the observer registered with `is_default=True` is used, or else the first one registered. If no observer is found (nothing registered, or a misspelled name), the method runs and nobody is notified, with no error.
- **`notify_before`** *`(bool)`*: Default `False`. `True` notifies before the method runs; `False` notifies after it returns. If the method raises, listeners set to run after it are not notified.

**Example**

```python
# your_core_lib/data_layers/service/user_service.py
from core_lib.data_layers.service.service import Service
from core_lib.observer.observer_decorator import Observe

from your_core_lib.constants import USER_OBSERVER
from your_core_lib.data_layers.data_access.user_data_access import UserDataAccess
from your_core_lib.user_observer_listener import UserObserverListener


class UserService(Service):
    def __init__(self, user_da: UserDataAccess):
        self._user_da = user_da

    @Observe(event_key=UserObserverListener.EVENT_USER_CHANGE, value_param_name='user_id', observer_name=USER_OBSERVER)
    def update(self, user_id: int, data: dict):
        self._user_da.update(user_id, data)
```

`your_core_lib.user.update(1, {User.name.key: 'Ada'})` updates the row, then the listener prints `user 1 changed`.

## When a listener fails

If a listener's `update()` raises, `Observer.notify()` logs the error and raises it again. Listeners attached after it are not called, and the exception reaches whoever called the decorated method.

With the default `notify_before=False`, the method has already run by then. In the example above, the row is updated and saved, and the caller still gets the listener's exception. If a listener failure must not affect the emitter, catch errors inside that listener's `update()`.

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="test_core_lib.html">Previous</a></button>
    <button class="pageNext-btn"><a href="core_lib_listener.html">Next</a></button>
</div>
