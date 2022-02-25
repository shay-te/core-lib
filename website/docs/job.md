---
id: job
title: Job
sidebar_label: Job
---


Core-Lib provides `core_lib.jobs.JobScheduler` class that can schedule `core_lib.jobs.Job` instances to run in a separate thread.

# Job class

`Job` class provide an abstract method called `run`. to create a custom Job simply do.

```python
class MyJob(Job):
    def run(self):
        self.core_lib.user.do_somthing()
```

The local variable `self.core_lib` will be automatically populated by `CoreLib` when running using configuration (see below).    
In case you want to create the job manually. pass the `CoreLib` instance using the job function `set_data_handler`, Or using the constructor.

Example: 
`my_job.set_data_handler(my_core_lib)` 


# JobScheduler class

`JobScheduler` provides 2 main functions 

````python
# Run the job, and repeat by frequency
def schedule(self, initial_delay: str, frequency: str, job: Job):
    ...
# Run the job a single time
def schedule_once(self, initial_delay: str, job: Job):
    ... 
````
`initial_delay` the initial time after which the `run()` function will be called for the first time.

`frequency` the time interval after which `run()` function will be called.

`job` is the instance of `Job` class created by user that implements `run()` and `initialized()`

The parameters `initial_delay` and `frequency` are string parsed by the library [pytimeparse](https://github.com/wroberts/pytimeparse).

### Usage
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

# Core-Lib Instance

When a `Job` is run by the configuration file, it will automatically populate the local `core_lib` variable of a job 