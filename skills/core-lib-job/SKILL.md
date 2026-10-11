---
name: core-lib-job
description: MANDATORY — load this skill BEFORE you add or change a background or scheduled job, a `Job` subclass, a `jobs:` YAML block, `load_jobs()`, or a timer/periodic/startup task in a *-core-lib; do not write it from memory. A job is a thin `Job` whose `run()` calls the CoreLib's services; it is declared in YAML and scheduled by `load_jobs()` in the main class.
---

# Background and scheduled jobs

A `Job` is a class with `initialized(data_handler)` and `run()`. You declare jobs in YAML, and
`CoreLib.load_jobs()` builds each one, hands it your CoreLib and schedules it on a timer thread. The
job then calls the **same services** routes call — it opens no session and builds no client (§9;
docs: *Job*).

**Know what it is not:** not cron (intervals are durations, not clock times), not a queue (nothing
is persisted; a restart starts every timer from zero), and not single-runner: **every process that
builds the CoreLib runs its own copy**, so four web workers run the job four times. For "every day
at 04:00", retries or exactly one runner, start the work from cron/Celery/APScheduler and call the
CoreLib the same way.

## 1. The job — `jobs/<name>_job.py`, file named after the class

```python
import logging

from core_lib.jobs.job import Job

logger = logging.getLogger(__name__)


class ThingDueJob(Job):
    def initialized(self, data_handler):
        self._foo_core_lib = data_handler        # the object mapped to this job's name in load_jobs()

    def run(self):
        notified = self._foo_core_lib.thing.notify_overdue_things()   # a service call, nothing else
        logger.info(f'notified {notified} overdue things')
```

`initialized()` and `run()` are both abstract. The constructor receives only the extra `handler`
keys from the YAML — pass config values that way, and reach services through `initialized()`.

## 2. The YAML — a MAPPING from job name to settings

```yaml
core_lib:
  foo_core_lib:
    jobs:
      thing_due:                       # the job's name: the key you map in load_jobs()
        initial_delay: startup         # REQUIRED; 'startup'/'boot' = 0s; else a pytimeparse duration
        frequency: 1d                  # optional; omit to run once; from the END of one run to the next start
        is_run_in_parallel: false      # optional; default false = skip a run while the same class still runs
        handler:
          _target_: foo_core_lib.jobs.thing_due_job.ThingDueJob   # must match the real module path
          batch_size: 500              # every other key -> ThingDueJob(batch_size=500)
```

- `jobs` is a mapping, **not a list**: the old list + `class:`/`params:` shape crashes `load_jobs()`.
- Durations are pytimeparse (`30s`, `5m`, `2h30m`, `1d`). Clock times do not work: unquoted `16:00`
  is the number 960 and fails; quoted `'16:00'` means 16 minutes. `frequency: None` is the string
  `'None'` and fails — leave the key out instead.
- A bad or missing `initial_delay` raises while the CoreLib is being built.

## 3. Wire it — last thing in `__init__` (core-lib-main)

```python
self.load_jobs(core_cfg.foo_core_lib.jobs, {'thing_due': self})
```

- The dict maps job name → what `initialized()` receives, usually the CoreLib (`self`). A job whose
  name is missing from it is still scheduled, but `initialized()` never runs and `run()` fails on
  every tick with an `AttributeError` that the scheduler only logs.
- Call it **last**: a `startup`/`0s` job runs as soon as `load_jobs()` schedules it — before
  `__init__` returns and before `start_core_lib()`.
- A job that is also a `CoreLibListener` is attached for you and gets `on_core_lib_ready()`.

## Runtime behaviour that bites

- **Jobs run on timer threads.** An in-memory SQLite database exists only in the thread that
  created it, so a scheduled job sees no tables. Real deployments use a database server; a local
  run uses an SQLite file.
- An exception in `run()` is caught and logged; a repeating job keeps its schedule. Nothing retries
  or alerts — `run()` reports its own failures if they matter.
- With `is_run_in_parallel: false` (default), a tick that arrives while a job **of the same class**
  is still running is skipped and logged.
- Timers are daemon threads: they do not keep the process alive.

## Testing

Never wait for the scheduler. Build the CoreLib from the test config, then run the job yourself:

```python
job = ThingDueJob()
job.set_data_handler(self.foo_core_lib)   # what load_jobs() does; calls initialized()
job.run()                                 # in the test's own thread, so in-memory SQLite works
```

Then assert the effect **through the public services** (core-lib-tests). If a `startup` job queries
a table as soon as it is scheduled, the test bootstrap must create the tables first: pre-create them
on the factory engine and run `install()` before building the lib (§9, §13.4). A job scheduled an
hour out simply never fires during the test.

## Rules to enforce

- One `Job` class per file in `jobs/`, the file named after the class; `run()` calls services only —
  no session, no DataAccess, no client of its own.
- YAML is a mapping with a required `initial_delay`; `_target_` matches the real module path.
- `load_jobs()` is the last line of `__init__`, with every job name mapped.
- Nothing in a job assumes it is the only runner, or that it runs at a clock time.
