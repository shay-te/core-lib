---
id: observer
title: Observer
sidebar_label: Observer
---

# Observer

*core_lib.observer.observer.Observer* [[source]](https://github.com/shay-te/core-lib/blob/5b8b2a4ca73dfd29138a216eb1f5648a5ae9be55/core_lib/observer/observer.py#L10)

Using the `Observer` class to `attach`, `detach`, `notify` to register events. 

## ObserverListener

*core_lib.observer.observer_listener.ObserverListener* [[source]](https://github.com/shay-te/core-lib/blob/5b8b2a4ca73dfd29138a216eb1f5648a5ae9be55/core_lib/observer/observer_listener.py#L4)


`ObserverListener` listener class to be implemented by the user. 

```python
from core_lib.observer.observer_listener import ObserverListener


class UserObserverListener(ObserverListener):

    EVENT_USER_CHANGE = "EVENT_USER_CHANGE"

    def update(self, key: str, value):
        if key == "":
            pass
```


## Settings up the observer

```python
from core_lib.core_lib import CoreLib
from core_lib.observer.observer_factory import ObserverRegistry
from core_lib.observer.observer import Observer
from core_lib.observer.observer_decorator import Observe

class MyCoreLib(CoreLib):

    def __init__(self, conf: DictConfig):
        self.config = conf

        main_observer = Observer()
        main_observer.attach(UserObserverListener())
        observer_factory = ObserverRegistry()
        observer_factory.register("main", main_observer)
        Observe.set_factory(observer_factory)
```


## Observe Decorator

*core_lib.observer.observer_decorator.Observe* [[source]](https://github.com/shay-te/core-lib/blob/5b8b2a4ca73dfd29138a216eb1f5648a5ae9be55/core_lib/observer/observer_decorator.py#L7)


```python
class Observe(object):

    def __init__(
        self, event_key: str, value_param_name: str = None, observer_name: str = None, notify_before: bool = False
    ):
```

**Arguments**

- **`event_key`** *`(str)`*: Event key to notify.
- **`value_param_name`** *`(str)`*: Default `None`, Event value parameter name, when specify will pass the parameter value otherwise will pass all parameters as a dictionary.
- **`observer_name`** *`(str)`*: Default `None`, When multiple observers register to the `ObserverRegistry`.
- **`notify_before`** *`(bool)`*: Default `False`, When to send the event before the func call or after.

**Example**

```python
class UserDataAccess(DataAccess):

    def __init__(self, db: SqlAlchemyDataHandlerFactory):
        self._db = db

    @Observe(event_key=UserObserverListener.EVENT_USER_CHANGE, notify_before=False)
    def update(self, user_id: int, update):
        with self._db.get() as session:
            session.query(User).filter(User.id == user_id).update(update)

```
