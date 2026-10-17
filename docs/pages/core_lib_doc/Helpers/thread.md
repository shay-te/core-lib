---
id: thread
title: Thread Utilities
sidebar: core_lib_doc_sidebar
permalink: thread.html
folder: core_lib_doc
toc: false
---

`LockGroup` gives you one `threading.Lock` per key: per user ID, per file path, per cache key. Two threads that ask for the same key get the same lock; threads working on different keys do not block each other.

> **Optional utility.** You can use Core-Lib without it. Over a plain `dict` of locks it adds two things: lock creation is itself thread-safe, and `clear()` removes locks that have not been used for a while. Entries are never removed on their own; they stay until you call `clear()`.
>
> **Where it fits:** Inside a Service, when concurrent calls for the same key must not interleave (for example, two requests updating the same user's balance in one worker).
>
> **In-process only.** These are `threading.Lock` objects held in memory. They serialize threads inside one Python process. They do not serialize requests handled by different worker processes or machines (several gunicorn/uwsgi workers, several pods). For that, use a database row lock or a distributed lock such as Redis.

*core_lib.helpers.thread.LockGroup* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/thread.py){:target="_blank"}

```python
class LockGroup(object):
    def __init__(self, max_age: timedelta):
```

**Arguments**

- **`max_age`** *`(timedelta)`*: How long since its last `get_lock()` call a lock must be before `clear()` may remove it. Nothing is removed until you call `clear()`.

**Example**

```python
from datetime import timedelta
from core_lib.helpers.thread import LockGroup

lock_group = LockGroup(max_age=timedelta(minutes=5))
```

## Functions

### get_lock()

*core_lib.helpers.thread.LockGroup.get_lock()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/thread.py#L15){:target="_blank"}

Returns the `threading.Lock` for `param`. The first call for a value creates the lock; later calls return the same lock. Each call also records the time, which is what `clear()` compares with `max_age`. Thread-safe.

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
balances = {}


def add_credit(user_id: int, amount: int):
    with user_locks.get_lock(user_id):
        # only one thread at a time per user_id; other users are not blocked
        balances[user_id] = balances.get(user_id, 0) + amount


add_credit(7, 5)
add_credit(7, 3)
print(balances)  # {7: 8}
print(user_locks.get_lock(7) is user_locks.get_lock(7))  # True
print(user_locks.get_lock(7) is user_locks.get_lock(8))  # False
```

### clear()

*core_lib.helpers.thread.LockGroup.clear()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/helpers/thread.py#L27){:target="_blank"}

Removes every lock whose last `get_lock()` call is older than `max_age`, unless the lock is held at that moment. `clear()` takes the group's own lock while it runs, so it does not race with `get_lock()`, and it never removes a lock that a thread is holding.

Without `clear()`, a `LockGroup` keeps one entry per key it has ever seen. If you lock on many different keys (every user ID, every file), call `clear()` from time to time, for example from a scheduled [job](job.html).

Choose a `max_age` far longer than a thread ever holds, or waits for, one lock. `clear()` checks whether a lock is held, not whether a thread is about to acquire it.

```python
def clear(self):
```

**Example**

```python
import time
from datetime import timedelta

from core_lib.helpers.thread import LockGroup

user_locks = LockGroup(max_age=timedelta(milliseconds=10))

held = user_locks.get_lock('user-1')
held.acquire()                        # a thread is inside its critical section
idle = user_locks.get_lock('user-2')  # created, then not used again
time.sleep(0.05)                      # both are now older than max_age

user_locks.clear()
print(user_locks.get_lock('user-1') is held)  # True: held, so clear() kept it
print(user_locks.get_lock('user-2') is idle)  # False: idle, removed; this is a new lock
held.release()
```

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="validation.html">Previous</a></button>
    <button class="pageNext-btn"><a href="constants.html">Next</a></button>
</div>
