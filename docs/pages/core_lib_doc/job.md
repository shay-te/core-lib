---
id: job
title: Job
sidebar: core_lib_doc_sidebar
permalink: job.html
folder: core_lib_doc
toc: false
---

A `Job` is a class with a `run()` method that Core-Lib calls on a background thread, once or at a fixed interval. You declare jobs in YAML. `CoreLib.load_jobs()` builds each job, gives it your `CoreLib` object and schedules it. The job then calls the same services your web routes call, so it does not open its own database session or build its own API clients.

**What it adds** over a plain `threading.Timer`: jobs are declared in config, each job receives your `CoreLib`, and by default a run is skipped while an earlier run of the same job class is still going.

**What it is not:** a cron daemon or a task queue. Intervals are durations (`30m`, `24h`), not clock times. Nothing is stored, so a restart starts every timer from zero. Every process that calls `load_jobs()` runs its own copy of each job: if each of four web workers builds your `CoreLib`, the job runs four times. If you need "every day at 04:00", retries, or exactly one runner across many processes, start the work from cron, Celery or APScheduler instead and have it call your `CoreLib` object the same way.

> **Where it fits:** One of the [six layers](index.html#the-layers). A `Job` calls into Services the same way a web route or test would.

---

## Example: suspend unpaid subscriptions every night

The admin page already calls `shop_core_lib.subscription.suspend_unpaid()`. A nightly job should do the same thing, without database code of its own. `SubscriptionService` is an ordinary service over a `Subscription` entity with `email`, `is_paid` and `is_active` columns, with the methods `create(email, is_paid)`, `get(subscription_id)` and `suspend_unpaid()` (see [Data Layers](data_layers.html) for how to write one).

### 1. Write the job

```python
# shop_core_lib/jobs/suspend_unpaid_job.py
import logging

from core_lib.jobs.job import Job

logger = logging.getLogger(__name__)


class SuspendUnpaidJob(Job):
    def initialized(self, data_handler):
        self.shop_core_lib = data_handler  # your CoreLib, passed in by load_jobs()

    def run(self):
        suspended = self.shop_core_lib.subscription.suspend_unpaid()
        logger.info(f'suspended {suspended} unpaid subscriptions')
```

`initialized()` and `run()` are both abstract, so every job defines them.

### 2. Declare it in YAML

```yaml
# shop_core_lib/config/shop_core_lib.yaml
core_lib:
  shop_core_lib:
    data:
      db:
        create_db: true
        url:
          protocol: sqlite
          file: shop.db              # a file, not in-memory SQLite: see step 3
    jobs:
      suspend_unpaid:                # the job's name: the key you map in load_jobs()
        initial_delay: 1h            # first run 1 hour after load_jobs()
        frequency: 24h               # then 24 hours after each run ends
        handler:
          _target_: shop_core_lib.jobs.suspend_unpaid_job.SuspendUnpaidJob
```

`jobs` is a mapping from job name to settings, not a list. Each job takes these keys:

| Key | Required | Meaning |
|---|---|---|
| `initial_delay` | yes | Time from `load_jobs()` to the first run, as a duration: `0s`, `30s`, `5m`, `2h30m`, `1d`. `startup` and `boot` mean `0s`. |
| `frequency` | no | Time from the end of one run to the start of the next. Leave it out to run the job once. |
| `is_run_in_parallel` | no | Default `false`: if a job of the same class is still running when this one is due, this run is skipped. See [JobScheduler](#jobscheduler-class). |
| `handler` | yes | `_target_` is the job class. Every other key is passed to its constructor: `recipient: ops@acme.com` next to `_target_` builds `YourJob(recipient='ops@acme.com')`. |

Durations are parsed by [pytimeparse](https://github.com/wroberts/pytimeparse){:target="_blank"}. Clock times do not work. YAML reads an unquoted `16:00` as the number 960, and `load_jobs()` fails on it. Quoted, `'16:00'` means 16 minutes. `frequency: None` fails too, because YAML reads it as the string `'None'`. To run a job once, leave `frequency` out.

### 3. Load it in your `CoreLib`

```python
# shop_core_lib/shop_core_lib.py
from omegaconf import DictConfig

from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.core_lib import CoreLib

from shop_core_lib.data_layers.data_access.subscription_data_access import SubscriptionDataAccess
from shop_core_lib.data_layers.service.subscription_service import SubscriptionService


class ShopCoreLib(CoreLib):
    def __init__(self, config: DictConfig):
        super().__init__()
        self.config = config
        db = SqlAlchemyConnectionFactory(config.core_lib.shop_core_lib.data.db)
        self.subscription = SubscriptionService(SubscriptionDataAccess(db))

        # Last: a job with a 0s delay can start before __init__ returns.
        self.load_jobs(config.core_lib.shop_core_lib.jobs, {'suspend_unpaid': self})
```

The second argument of `load_jobs()` maps each job name to the object that job receives in `initialized()`. A job whose name is missing from this map is still scheduled, but its `initialized()` is never called. Its `run()` then fails on `self.shop_core_lib`, and the scheduler only logs the `AttributeError`. Projects made by `core_lib generate` start with an empty map (`jobs_data_handlers = {}`), so add an entry for each job.

Jobs run on their own threads. An in-memory SQLite database exists only in the thread that created it, so a scheduled job finds no tables (`no such table: subscription`). Use an SQLite file, as above, or a database server.

### 4. Test it without waiting for the scheduler

In a test, run the job yourself:

```python
# tests/test_suspend_unpaid_job.py
import unittest

from core_lib.helpers.test import load_core_lib_config

from shop_core_lib.data_layers.data.db.entities.subscription import Subscription
from shop_core_lib.jobs.suspend_unpaid_job import SuspendUnpaidJob
from shop_core_lib.shop_core_lib import ShopCoreLib


class TestSuspendUnpaidJob(unittest.TestCase):

    def setUp(self):
        self.shop_core_lib = ShopCoreLib(load_core_lib_config('./config', 'test_config.yaml'))

    def test_suspends_only_unpaid(self):
        paid = self.shop_core_lib.subscription.create('cfo@acme.com', is_paid=True)
        unpaid = self.shop_core_lib.subscription.create('ops@globex.com', is_paid=False)

        job = SuspendUnpaidJob()
        job.set_data_handler(self.shop_core_lib)  # what load_jobs() does
        job.run()                                 # run it now, in this thread

        self.assertTrue(self.shop_core_lib.subscription.get(paid[Subscription.id.key])[Subscription.is_active.key])
        self.assertFalse(self.shop_core_lib.subscription.get(unpaid[Subscription.id.key])[Subscription.is_active.key])
```

```yaml
# tests/config/test_config.yaml
defaults:
  - shop_core_lib                  # the production YAML
  - _self_                         # then the changes below

hydra:
  searchpath:
    - pkg://shop_core_lib.config   # where Hydra finds shop_core_lib.yaml

core_lib:
  shop_core_lib:
    data:
      db:
        url:
          file: null               # no file: in-memory SQLite
```

Building `ShopCoreLib` in `setUp()` also schedules the job, but its first run is an hour away, so it never fires during the test. The test calls `run()` in its own thread, which is why in-memory SQLite works here. `pkg://shop_core_lib.config` needs a `shop_core_lib/config/__init__.py` file. [Testing Core-Lib](test_core_lib.html) explains the test config in more detail.

---

## load_jobs()

*core_lib.core_lib.CoreLib.load_jobs()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/core_lib.py#L30){:target="_blank"}

```python
def load_jobs(self, config: DictConfig, job_to_data_handler: dict = {}):
```

**Arguments**

- **`config`** *`(DictConfig)`*: The `jobs` mapping (job name to settings), for example `config.core_lib.shop_core_lib.jobs`. It must contain at least one job.
- **`job_to_data_handler`** *`(dict)`*: Job name to the object passed to that job's `initialized()`. Usually your `CoreLib` (`self`).

**What it does, for each job**

1. Builds the class named in `handler._target_`, passing the other `handler` keys to its constructor. Raises `ValueError` if the class is not a `Job`.
2. Reads `initial_delay`, which is required, and turns `startup` or `boot` into `0s`.
3. If the job's name is a key in `job_to_data_handler`, calls `job.set_data_handler(...)`, which calls `initialized()`.
4. Schedules it on `CoreLib.scheduler`: as a repeating job if it has a `frequency`, otherwise to run once. `is_run_in_parallel` defaults to `false` in both cases.
5. If the job is also a [`CoreLibListener`](core_lib_listener.html), attaches it to your `CoreLib`, so it gets `on_core_lib_ready()` when you call `start_core_lib()`.

The countdown starts when `load_jobs()` runs, not when you call `start_core_lib()`. A bad duration (`initial_delay: tomorrow`) or a missing `initial_delay` raises an error here, while your `CoreLib` is being built. `load_jobs()` does not return the jobs; they run until the process exits.

---

## Job class

*core_lib.jobs.job.Job* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/jobs/job.py#L4){:target="_blank"}

Extend `Job` and implement two methods:

- **`initialized(self, data_handler)`**: receives the object mapped to this job's name in `load_jobs()`, usually your `CoreLib`. Save it.
- **`run(self)`**: does the work, by calling your services through the saved object.

`set_data_handler(data_handler)` calls `initialized()`. `load_jobs()` calls it for you. Call it yourself when you create a job in code, as in a test or with `JobScheduler`:

```python
job.set_data_handler(your_core_lib)
```

The constructor only receives the extra `handler` keys from the YAML. Pass config values that way, and get services through `initialized()`.

---

## JobScheduler class

*core_lib.jobs.job_scheduler.JobScheduler* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/jobs/job_scheduler.py#L10){:target="_blank"}

Runs `Job` objects on `threading.Timer` threads. `load_jobs()` uses `CoreLib.scheduler`, one scheduler shared by every `CoreLib` in the process. You can also call a scheduler yourself, for example to run a one-off job when something happens.

```python
def schedule(self, initial_delay: str, frequency: str, job: Job, is_run_in_parallel: bool = False):

def schedule_once(self, initial_delay: str, job: Job, is_run_in_parallel: bool = True, params: dict = {}):

def stop(self, job: Job):
```

**Arguments**

- **`initial_delay`** *`(str)`*: Time until the first run, as a pytimeparse duration: `'0s'`, `'1s'`, `'2h30m'`. `startup` and `boot` only work in the YAML read by `load_jobs()`. Here, pass `'0s'`.
- **`frequency`** *`(str)`*: Time from the end of one run to the start of the next.
- **`job`** *`(Job)`*: The job. If `run()` uses the handler, call `set_data_handler()` first.
- **`is_run_in_parallel`** *`(bool)`*: Default `False` for `schedule()` and `True` for `schedule_once()`. See below.
- **`params`** *`(dict)`*: Keyword arguments for `run()`. `params={'user_id': 7}` calls `job.run(user_id=7)`.

**Behaviour**

- With `is_run_in_parallel=False`, a run that is due while another job of the same class is still running is skipped and logged (`job ... is already running, ignoring this run`). The check is by class name, so it covers every instance of that class on the same scheduler. A repeating job tries again after `frequency`; a one-time job is dropped. With `True`, runs can overlap.
- An exception in `run()` is caught and logged. A repeating job keeps its schedule.
- `stop(job)` cancels the next run. A run that has already started finishes.
- The timers are daemon threads, so they do not keep the process alive. A script that only schedules jobs must keep its main thread running.

**Example**

```python
import time

from core_lib.jobs.job import Job
from core_lib.jobs.job_scheduler import JobScheduler


class Heartbeat(Job):
    def initialized(self, data_handler):
        self.core_lib = data_handler

    def run(self):
        print('tick')


class SendWelcomeEmail(Job):
    def initialized(self, data_handler):
        self.core_lib = data_handler

    def run(self, user_id: int):  # schedule_once(params=...) passes keyword arguments
        print(f'welcome email for user {user_id}')


scheduler = JobScheduler()

heartbeat = Heartbeat()
heartbeat.set_data_handler(your_core_lib)  # load_jobs() does this for you
scheduler.schedule('0s', '1s', heartbeat)  # now, then 1 second after each run ends
time.sleep(2.5)
scheduler.stop(heartbeat)                  # no more runs

welcome = SendWelcomeEmail()
welcome.set_data_handler(your_core_lib)
scheduler.schedule_once('0s', welcome, params={'user_id': 7})
time.sleep(0.5)
```

`your_core_lib` is your `CoreLib` object. The `time.sleep()` calls keep the script alive long enough for the jobs to run. It prints:

```text
tick
tick
tick
welcome email for user 7
```

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="cache.html">Previous</a></button>
    <button class="pageNext-btn"><a href="middleware.html">Next</a></button>
</div>
