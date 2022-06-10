---
id: core_lib
title: Core Lib Class
sidebar_label: Core Lib Class
---

*core_lib.core_lib.CoreLib* [[source]](https://github.com/shay-te/core-lib/blob/058dead7fa30e1a2b4531f698da95c5380ca8d55/core_lib/core_lib.py#L17)

This is the main `Core-Lib` class, all the `Core-Libs` extend this class. This class provides various functions that other `Core-Libs` can use to carry out various important tasks.

## Usage 
```python
from core_lib.core_lib import CoreLib

class YourCoreLib(CoreLib):
    def __init__(self, config: DictConfig):
        ...
```

## init()

*core_lib.core_lib.CoreLib.\_\_init\_\_()* [[source]](https://github.com/shay-te/core-lib/blob/058dead7fa30e1a2b4531f698da95c5380ca8d55/core_lib/core_lib.py#L22)

Here we just initialize a private `Observer` with the `listener_type` as `CoreLibListener` and a private variable `_core_lib_started`.

```python
def __init__(self):
    self._core_lib_started = False
    self._observer = Observer(listener_type=CoreLibListener)
```

## Functions

### load_jobs()

*core_lib.core_lib.CoreLib.load_jobs()* [[source]](https://github.com/shay-te/core-lib/blob/058dead7fa30e1a2b4531f698da95c5380ca8d55/core_lib/core_lib.py#L26)

Used to load instantiate all the jobs present in the config file using `instantiate_config_group_generator_dict` and start to schedule them based on the frequency.

```python
def load_jobs(self, config: DictConfig, job_to_data_handler: dict = {}):
```

**Arguments**

- **`config`** *`(DictConfig)`*: `jobs` sections from the `Core-Lib` config.
- **`job_to_data_handler`** *`(dict)`*: Data handlers for the jobs listed in the config, the `key` should be the `job name` and the `value` should be the `handler name`.

**Example**

```python
from core_lib.core_lib import CoreLib

class YourCoreLib(CoreLib):
   def __init__(self, config: DictConfig):
        ...
        self.load_jobs(self.config.core_lib.your_core_lib.jobs, {'job_name': self,...})
```

### attach_listener()

*core_lib.core_lib.CoreLib.attach_listener()* [[source]](https://github.com/shay-te/core-lib/blob/058dead7fa30e1a2b4531f698da95c5380ca8d55/core_lib/core_lib.py#L60)

Attaches a `CoreLibListener` implemented class to the private observer `self._observer` created in the `init`.

```python
def attach_listener(self, core_lib_listener: CoreLibListener):
```

**Arguments**

- **`core_lib_listener`** *`(CoreLibListener)`*: A inherited class that implements the abstract functions in `CoreLibListener`.

**Example**

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

### detach_listener()

*core_lib.core_lib.CoreLib.detach_listener()* [[source]](https://github.com/shay-te/core-lib/blob/058dead7fa30e1a2b4531f698da95c5380ca8d55/core_lib/core_lib.py#L63)

Detaches a `CoreLibListener` implemented class from the private observer `self._observer` created in the `init`.

```python
def detach_listener(self, core_lib_listener: CoreLibListener):
```

**Arguments**

- **`core_lib_listener`** *`(CoreLibListener)`*: A inherited class that implements the abstract functions in `CoreLibListener`.

**Example**

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
core_lib.detach_listener(Listener())
```

### fire_core_lib_ready()

*core_lib.core_lib.CoreLib.fire_core_lib_ready()* [[source]](https://github.com/shay-te/core-lib/blob/058dead7fa30e1a2b4531f698da95c5380ca8d55/core_lib/core_lib.py#L66)

Notifies the observer listener with key `CoreLibListener.CoreLibEventType.CORE_LIB_READY` and value `None` and calls the implemented `on_core_lib_ready` function from the attached listener. This function is called in the `start_core_lib()` function. 

```python
def fire_core_lib_ready(self):
```

### fire_core_lib_destroy()

*core_lib.core_lib.CoreLib.fire_core_lib_destroy()* [[source]](https://github.com/shay-te/core-lib/blob/058dead7fa30e1a2b4531f698da95c5380ca8d55/core_lib/core_lib.py#L69)

Notifies the observer listener with key `CoreLibListener.CoreLibEventType.CORE_LIB_DESTROY` and value `None` and calls the implemented `on_core_lib_destroy` function from the attached listener. This function is called in the `__del__` method of the class. 

```python
def fire_core_lib_destroy(self):
```

### start_core_lib()

*core_lib.core_lib.CoreLib.start_core_lib()* [[source]](https://github.com/shay-te/core-lib/blob/058dead7fa30e1a2b4531f698da95c5380ca8d55/core_lib/core_lib.py#L73)

Calls the `fire_core_lib_ready()` function and also sets the value of the private variable `self._core_lib_started` created in the `init` to `True` .

```python
def start_core_lib(self):
```
**Example**

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
core_lib.start_core_lib()
```

### \_\_del\_\_()

*core_lib.core_lib.CoreLib.start_core_lib()* [[source]](https://github.com/shay-te/core-lib/blob/058dead7fa30e1a2b4531f698da95c5380ca8d55/core_lib/core_lib.py#L81)

Destructor method of the class, calls `fire_core_lib_destroy()` function.

```python
def __del__(self):
```
**Example**

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

del core_lib
```