---
id: observer
title: Observer
sidebar_label: Observer
---

Using the `Oserver` class to `attach`, `detache`, `notify` to register events. 

`ObserverListener` listener class to be implemented by the user. 
```python
from core_lib.observer.observer_listener import ObserverListener


class UserObserverListener(ObserverListener):

    EVENT_USER_CHANGE = "EVENT_USER_CHANGE"

    def update(self, key: str, value):
        if key == "":
            pass
```


# Settings up the observer

```python
from core_lib.core_lib import CoreLib
from core_lib.observer.observer_factory import ObserverFactory
from core_lib.observer.observer import Observer
from core_lib.observer.observer_decorator import Observe

class MyCoreLib(CoreLib):

    def __init__(self, conf: DictConfig):
        self.config = conf

        main_observer = Observer()
        main_observer.attach(UserObserverListener())
        observer_factory = ObserverFactory()
        observer_factory.register("main", main_observer)
        Observe.set_factory(observer_factory)
```


# Observe decorator

```python
class UserDataAccess(DataAccess):

    def __init__(self, db: DBDataSessionFactory):
        self._db = db

    @Observe(event_key=UserObserverListener.EVENT_USER_CHANGE, notify_before=False)
    def update(self, user_id: int, update):
        with self._db.get() as session:
            session.query(User).filter(User.id == user_id).update(update)

```


### Observe.\_\_init\_\_
`value_rule_validators` a list of `ValueRuleValidator` objects. 

`event_key` event key to notify  (type: `str`, default: `None`)

`value_param_name` event value parameter name, when specify will pass the parameter value otherwise will pass all parameters as `dict` (type: `str`, default: `None`)
  
`observer_name` when multiple observers register to the `ObserverFactory`. (type: `str`, default: `None`)
 
`notify_before` when to send the event before the func call or after (type: `bool`, default: `False`)

