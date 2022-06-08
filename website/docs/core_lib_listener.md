---
id: core_lib_listener
title: Core Lib Listener
sidebar_label: Core Lib Listener
---

*core_lib.core_lib.CoreLibListner* [[source]](https://github.com/shay-te/core-lib/blob/058dead7fa30e1a2b4531f698da95c5380ca8d55/core_lib/core_lib_listener.py#L7)

An abstract class that implements `ObserverListener`, functions provided by this class are used by the `CoreLib` class methods.

## Functions

### on_core_lib_ready()

*core_lib.core_lib.CoreLibListner.on_core_lib_ready()* [[source]](https://github.com/shay-te/core-lib/blob/058dead7fa30e1a2b4531f698da95c5380ca8d55/core_lib/core_lib_listener.py#L13)

Abstract method that will be called in the [`start_core_lib()`](core_lib#start_core_lib) function and should take care of the task to be performed at the start of the `Core-Lib`.

```python
@abstractmethod
def on_core_lib_ready(self):
```

### on_core_lib_destroy()

*core_lib.core_lib.CoreLibListner.on_core_lib_destroy()* [[source]](https://github.com/shay-te/core-lib/blob/058dead7fa30e1a2b4531f698da95c5380ca8d55/core_lib/core_lib_listener.py#L13)

Abstract method that will be called in the [destructor](core_lib#del) of the `CoreLib` class and should take care of the cleanups to be performed.

```python
@abstractmethod
def on_core_lib_destroy(self):
```

### update()

*core_lib.core_lib.CoreLibListner.update()* [[source]](https://github.com/shay-te/core-lib/blob/058dead7fa30e1a2b4531f698da95c5380ca8d55/core_lib/core_lib_listener.py#L13)

An implemented method from the `ObserverListener` class, this method takes care of calling the respective functions [`on_core_lib_ready()`](core_lib_listener#on_core_lib_ready) and [`on_core_lib_destroy()`](core_lib_listener#on_core_lib_destroy) on `key` change.

```python
def update(self, key: str, value):
```

**Arguments**

- **`key`** *`(str)`*: The key that the listener listens to for changes.
- **`value`**: Any value to be stored.

**Example**

Implementation of a `CoreLibListener` class.

```python
from core_lib.core_lib_listener import CoreLibListener
from core_lib.core_lib import CoreLib

class YourCoreLib(CoreLib):
   def __init__(self, config: DictConfig):
        ...
        self.load_jobs(self.config.core_lib.your_core_lib.jobs, {'job_name': self,...})

class Listener(CoreLibListener):

    def on_core_lib_ready(self):
        # Do some task here
        pass

    def on_core_lib_destroy(self):
        # Cleanups here
        pass

core_lib = YourCoreLib(config)
core_lib.attach_listener(Listener())
```