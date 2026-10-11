---
name: core-lib-observer
description: MANDATORY — load this skill BEFORE you add or change events a *-core-lib fires for its host — a listener ABC, an `ObserverListener` adapter, `EVENT_*` keys, `@Observe`, `_fire_*` methods, `attach_<name>_listener` — or a `CoreLibListener` lifecycle hook (`on_core_lib_ready`/`on_core_lib_destroy`); do not write it from memory. Events let a host react to what the library did without the library knowing the host.
---

# Events a host can react to (Observer)

A library must not call host code, yet a host often needs to react ("a thing was created" → send an
email). The library fires a named event; the host attaches a listener. Four pieces, exactly as the
older libs do it (§8; docs: *Observer*, *CoreLib Listener*).

## 1. `observer/foo_listener.py` — the interface the HOST implements

```python
from abc import ABC, abstractmethod


class FooListener(ABC):
    """Implement in the host and attach with FooCoreLib.attach_foo_listener().

    Listeners run synchronously, after the library's write has committed. An exception raised here
    reaches the caller of the service method even though the data is already saved, so catch your
    own errors and queue slow work instead of doing it inline. Delivery is at most once.
    """

    @abstractmethod
    def on_thing_due(self, thing: dict):          # mandatory event
        ...

    def on_thing_created(self, thing: dict):      # optional events get empty default bodies
        pass
```

## 2. `observer/foo_observer_listener.py` — the adapter and the event keys

```python
from core_lib.observer.observer_listener import ObserverListener

from foo_core_lib.observer.foo_listener import FooListener


class FooObserverListener(ObserverListener):
    EVENT_THING_CREATED = 'EVENT_THING_CREATED'
    EVENT_THING_DUE = 'EVENT_THING_DUE'

    def __init__(self, foo_listener: FooListener):
        self._foo_listener = foo_listener

    def update(self, key: str, value):
        # `value` is the dict of the _fire_* method's arguments by parameter name, so these keys
        # ARE its parameter names: rename a parameter and rename the key here (see AGENTS.md).
        if key == self.EVENT_THING_CREATED:
            self._foo_listener.on_thing_created(value['thing'])
        elif key == self.EVENT_THING_DUE:
            self._foo_listener.on_thing_due(value['thing'])
```

## 3. Wire it in the main class (core-lib-main)

```python
from core_lib.observer.observer import Observer

from foo_core_lib.constants import FOO_CORE_LIB_NAME   # 'FOO_CORE_LIB'

# inside FooCoreLib.__init__
if not CoreLib.observer_registry.get(FOO_CORE_LIB_NAME):
    CoreLib.observer_registry.register(FOO_CORE_LIB_NAME, Observer())
self._foo_observer = CoreLib.observer_registry.get(FOO_CORE_LIB_NAME)   # the REGISTERED one


def attach_foo_listener(self, foo_listener: FooListener):              # named after the domain
    self._foo_observer.attach(FooObserverListener(foo_listener))
```

- **Read the registered observer back.** `@Observe` notifies whatever the registry holds under the
  name. If you keep a fresh `Observer()` and only register it when the name is free, a second
  construction in the process attaches the host's listener to an observer nobody notifies — silently.
- Never shadow `CoreLib.attach_listener` (that is the lifecycle hook below); name the method after
  the domain: `attach_task_listener`, `attach_workflow_listener`, `attach_foo_listener`.

## 4. Fire from the service — an empty `_fire_*` method under `@Observe`

```python
from core_lib.data_layers.service.service import Service
from core_lib.data_transform.result_to_dict import ResultToDict, result_to_dict
from core_lib.error_handling.duplicate_error_decorator import DuplicateErrorHandler
from core_lib.observer.observer_decorator import Observe

from foo_core_lib.constants import FOO_CORE_LIB_NAME
from foo_core_lib.observer.foo_observer_listener import FooObserverListener


class ThingService(Service):
    @ResultToDict()
    @DuplicateErrorHandler()
    def create(self, data: dict):
        thing = result_to_dict(self._thing_da.create(data))
        self._fire_on_thing_created(thing)           # after the write: the event describes saved data
        return thing

    @Observe(event_key=FooObserverListener.EVENT_THING_CREATED, observer_name=FOO_CORE_LIB_NAME)
    def _fire_on_thing_created(self, thing: dict):
        pass                                          # the decorator does the dispatch
```

The payload is a `@ResultToDict`-style dict (`thing[Thing.id.key]`), never an ORM row — a host never
holds an entity.

## What `@Observe` actually does

- With no `value_param_name`, listeners get a dict of **all** the call's arguments by parameter name,
  `self` and defaults included. With `value_param_name='thing'` they get that one argument — but the
  caller must pass it **positionally**, or the decorator raises `IndexError`.
- **Always pass `observer_name`.** A name that is not registered notifies nobody and raises nothing.
  With no name at all, it uses the default or the **first observer registered in the process** —
  in a host that composes several libs, possibly another library's.
- `notify_before=False` (default) notifies after the method returns; if the method raises, nobody is
  notified.
- `Observer.notify` calls listeners in attach order. If one raises, it is logged and **re-raised**:
  later listeners are skipped and the service call fails after its write committed. A
  compare-and-set retry around such a call loses the event — delivery is at most once. Exactly-once
  needs a transactional outbox (§A4).

## Lifecycle: `CoreLibListener`

For "the CoreLib is ready / is going away", implement `CoreLibListener.on_core_lib_ready()` and
`on_core_lib_destroy()` and attach it with `attach_listener()`. `start_core_lib()` fires
`on_core_lib_ready()` (once — a second call raises `CoreLibInitException`); `__del__` fires
`on_core_lib_destroy()`, which Python does not guarantee at interpreter exit, so never rely on it for
cleanup that must happen. A `Job` that is also a `CoreLibListener` is attached by `load_jobs()`.

## Testing

Attach a recording `FooListener` through `attach_foo_listener`, call the public service, and assert
the events and their payloads (read with `Entity.col.key`). Also assert the failure contract you
document: a listener that raises makes the service call raise, and the row is still there.

## Rules to enforce

- Four pieces: host ABC, adapter with `EVENT_*` keys, guarded registration read back + typed
  `attach_<domain>_listener`, empty `_fire_*` methods under `@Observe(observer_name=...)`.
- Fire after the write, with dict payloads; never pass an entity.
- The listener ABC's docstring states the contract: synchronous, post-commit, at most once,
  exceptions reach the caller.
