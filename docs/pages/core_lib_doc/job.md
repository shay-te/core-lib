---
id: job
title: Job
sidebar: core_lib_doc_sidebar
permalink: job.html
folder: core_lib_doc
toc: false
---



# Configuration 

Jobs can be configured to run from the `core_lib.yaml` file. for example: 

`CoreLib` to run this job at startup by providing the `initial_deplay` parameter with one of the values `boot` or `startup` 

```yaml
core_lib:
  ...
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



### load_jobs()

*core_lib.core_lib.CoreLib.load_jobs()* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/core_lib.py#L26){:target="_blank"}

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





Core-Lib provides `core_lib.jobs.JobScheduler` class that can schedule `core_lib.jobs.Job` instances to run in a separate thread.

# Job class

*core_lib.jobs.job.Job* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/jobs/job.py#L4){:target="_blank"}

`Job` class provide an abstract method called `run`. to create a custom Job simply do.

```python
class MyJob(Job):
    def run(self):
        self.core_lib.user.do_somthing()
```

The local variable `self.core_lib` will be automatically populated by `CoreLib` when running using configuration (see below).    
In case you want to create the job manually. pass the `CoreLib` instance using the job function `set_data_handler`, Or using the constructor.

**Example**
`my_job.set_data_handler(my_core_lib)` 


# JobScheduler class

*core_lib.jobs.job_scheduler.JobScheduler* [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/jobs/job_scheduler.py#L10){:target="_blank"}

`JobScheduler` provides 2 main functions 

1. `schedule()` 
*core_lib.jobs.job_scheduler.JobScheduler.schedule() * [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/jobs/job_scheduler.py#L22){:target="_blank"}

2. `schedule_once()` 
*core_lib.jobs.job_scheduler.JobScheduler.schedule_once() * [[source]](https://github.com/shay-te/core-lib/blob/master/core_lib/jobs/job_scheduler.py#L27){:target="_blank"}

````python
# Run the job, and repeat by frequency
def schedule(self, initial_delay: str, frequency: str, job: Job):
    ...
# Run the job a single time
def schedule_once(self, initial_delay: str, job: Job):
    ... 
````

**Arguments**

- **`initial_delay`** *`(str)`*: The initial time after which the `run()` function will be called for the first time.
- **`frequency`** *`(str)`*: The time interval after which `run()` function will be called.
- **`job`** *`(Job)`*: Is the instance of `Job` class created by user that implements `run()` and `initialized()`

The parameters `initial_delay` and `frequency` are string parsed by the library [pytimeparse](https://github.com/wroberts/pytimeparse){:target="_blank"}.

**Example**
```python
from core_lib.jobs.job import Job
from core_lib.jobs.job_scheduler import JobScheduler

class UpdateCache(Job):

    def initialized(self, data_handler):
        pass

    def run(self):
        # code to update your cache

scheduler = JobScheduler()
job = UpdateCache()
# updates the cache 1 second after the schedule_once() is called
scheduler.schedule_once('1s', job)

# updates the cache 1 second after the job is scheduled and keeps updating every 30 minutes until stop() is called.
scheduler.schedule('1s', '30m', job) 

scheduler.stop()# stops the ongoing job schedule 
```
>If a job fails while running the `Exception` and the message will be logged by the `JobScheduler` for the same.



# Core-Lib Instance

When a `Job` is run by the configuration file, it will automatically populate the local `core_lib` variable of a job 

<div style="margin-top:2em">
    <button class="pagePrevious-btn"><a href="/cache.html"><< Previous</a></button>
    <button class="pageNext-btn"><a href="/connection.html">Next >></a></button>
</div>