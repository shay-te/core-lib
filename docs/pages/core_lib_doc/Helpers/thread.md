---
id: thread
title: Thread Utilities
sidebar: core_lib_doc_sidebar
permalink: thread.html
folder: core_lib_doc
toc: false
---

Per-resource locking — locking on a user ID, a file path, or a cache key — requires a lock per value, not one global lock. `LockGroup` maintains a dictionary of `threading.Lock` objects keyed by an arbitrary parameter and automatically evicts entries that haven't been used recently.

*core_lib.helpers.thread.LockGroup* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/thread.py){:target="_blank"}

```python
class LockGroup(object):
    def __init__(self, max_age: timedelta):
```

**Arguments**

- **`max_age`** *`(timedelta)`*: How long an unused lock entry is kept before `clear()` removes it.

**Example**

```python
from datetime import timedelta
from core_lib.helpers.thread import LockGroup

lock_group = LockGroup(max_age=timedelta(minutes=5))
```

## Functions

### get_lock()

*core_lib.helpers.thread.LockGroup.get_lock()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/thread.py#L15){:target="_blank"}

Returns the `threading.Lock` associated with `param`. Creates a new lock on the first call for a given value; returns the same lock on subsequent calls. Thread-safe.

```python
def get_lock(self, param) -> object:
```

**Arguments**

- **`param`**: The key identifying which lock to return. Can be any hashable value — an int ID, a string path, etc.

**Returns**

*`(threading.Lock)`*: The lock for this `param` value.

**Example**

```python
from datetime import timedelta
from core_lib.helpers.thread import LockGroup

user_locks = LockGroup(max_age=timedelta(minutes=10))

def update_user(user_id: int):
    with user_locks.get_lock(user_id):
        # only one thread at a time per user_id
        ...
```

### clear()

*core_lib.helpers.thread.LockGroup.clear()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/thread.py#L24){:target="_blank"}

Removes all lock entries that haven't been accessed within `max_age`. Call this periodically (e.g. from a background job) to prevent unbounded memory growth when the key space is large.

```python
def clear(self):
```

**Example**

```python
from datetime import timedelta
from core_lib.helpers.thread import LockGroup

user_locks = LockGroup(max_age=timedelta(minutes=5))

# called from a scheduled cleanup job
user_locks.clear()
```

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/validation.html"><< Previous</a></button>
    <button class="pageNext-btn"><a href="/constants.html">Next >></a></button>
</div>
