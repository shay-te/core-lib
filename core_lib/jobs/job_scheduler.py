from threading import Lock, Timer
from pytimeparse import parse
from core_lib.jobs.job import Job


class JobScheduler(object):

    def __init__(self):
        self._lock = Lock()
        self._job_to_timer = {}

    def stop(self, job: Job):
        self._lock.acquire()
        timer = self._job_to_timer.get(job)
        if timer:
            timer.cancel()
        self._lock.release()

    def schedule(self, initial_delay: str, frequency: str, job: Job):
        self._validate(initial_delay, job)
        self._validate_str_time(frequency, 'frequency')
        self._schedule(initial_delay, frequency, job)

    def schedule_once(self, initial_delay: str, job: Job):
        self._validate(initial_delay, job)
        self._schedule(initial_delay, None, job)

    def _schedule(self, initial_delay: str, frequency: str, job: Job):
        self._lock.acquire()
        timer = Timer(parse(initial_delay), self._run_job, kwargs={'job': job, 'frequency': frequency})
        timer.daemon = True
        self._job_to_timer[job] = timer
        timer.start()
        self._lock.release()

    def _run_job(self, job: Job, frequency: str):
        job.run()
        del self._job_to_timer[job]
        if frequency:
            self._schedule(frequency, frequency, job)

    def _validate(self, initial_delay: str, job: Job):
        assert job
        assert isinstance(job, Job)
        self._validate_str_time(initial_delay, 'initial_delay')

    def _validate_str_time(self, str_time: str, variable_name: str):
        error_msg = '{} `{}` is invalid'.format(variable_name, str_time)
        assert str_time, error_msg
        initial_delay_seconds = parse(str_time)
        assert initial_delay_seconds is not None, error_msg
