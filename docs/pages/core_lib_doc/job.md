---
id: job
title: Job
sidebar: core_lib_doc_sidebar
permalink: job.html
folder: core_lib_doc
toc: false
---

Background tasks often need to call the same services as your web routes, but they should not create their own database sessions or clients. A `Job` receives the handler it needs at startup, then `CoreLib` schedules it.

> **Where it fits:** One of the [six layers](/index.html#the-layers). A `Job` calls into Services the same way a web route or test would.

---

## Configuration

Jobs are declared in `core_lib.yaml` and loaded at startup via `load_jobs()`.

```yaml
core_lib:
  jobs:
    - initial_delay: 2h32m
      frequency: 16:00
      handler:
        class: some_package.MyJob
        params:
          some_param: some value

    - initial_delay: startup
      frequency: None
      handler:
        class: some_package.SomeJob
        params:
```

Use `initial_delay: startup` or `initial_delay: boot` to run a job immediately when `CoreLib` starts.

---

### load_jobs()

*core_lib.core_lib.CoreLib.load_jobs()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/core_lib.py#L26){:target="_blank"}

Reads the `jobs` config section, instantiates each job class, and schedules them.

```python
def load_jobs(self, config: DictConfig, job_to_data_handler: dict = {}):
```

**Arguments**

- **`config`** *`(DictConfig)`*: The `jobs` section from the `Core-Lib` config.
- **`job_to_data_handler`** *`(dict)`*: Maps each job name to its `CoreLib` handler instance.

**Example**

```python
class YourCoreLib(CoreLib):
    def __init__(self, config: DictConfig):
        super().__init__()
        ...
        self.load_jobs(self.config.core_lib.your_core_lib.jobs, {'job_name': self})
```

---

## Job class

*core_lib.jobs.job.Job* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/jobs/job.py#L4){:target="_blank"}

Extend `Job`, save the injected handler in `initialized()`, then use it from `run()`. The handler can be the `CoreLib` instance or a smaller object dedicated to that job.

```python
class MyJob(Job):
    def initialized(self, data_handler):
        self.core_lib = data_handler

    def run(self):
        self.core_lib.user.do_something()
```

To inject the `CoreLib` instance manually (when not using config):

```python
my_job.set_data_handler(my_core_lib)
```

---

## JobScheduler class

*core_lib.jobs.job_scheduler.JobScheduler* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/jobs/job_scheduler.py#L10){:target="_blank"}

Schedules `Job` instances to run in a background thread.

```python
# Run once after initial_delay
def schedule_once(self, initial_delay: str, job: Job):

# Run repeatedly after initial_delay, every frequency interval
def schedule(self, initial_delay: str, frequency: str, job: Job):
```

**Arguments**

- **`initial_delay`** *`(str)`*: Time before the first `run()` call. Parsed by [pytimeparse](https://github.com/wroberts/pytimeparse){:target="_blank"} — e.g. `'1s'`, `'2h30m'`, `'startup'`.
- **`frequency`** *`(str)`*: Interval between repeat calls.
- **`job`** *`(Job)`*: A `Job` instance implementing `run()`.

**Example**

```python
from core_lib.jobs.job import Job
from core_lib.jobs.job_scheduler import JobScheduler

class UpdateCache(Job):

    def initialized(self, data_handler):
        self.core_lib = data_handler

    def run(self):
        self.core_lib.user.refresh_cache()

scheduler = JobScheduler()
job = UpdateCache()

scheduler.schedule_once('1s', job)          # runs once, 1 second after call
scheduler.schedule('1s', '30m', job)        # runs every 30 minutes, starting 1 second after call

scheduler.stop(job)  # stops the scheduled job
```

> If a job raises an exception during `run()`, it is caught, logged by `JobScheduler`, and the schedule continues.

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/cache.html">Previous</a></button>
    <button class="pageNext-btn"><a href="/middleware.html">Next</a></button>
</div>
