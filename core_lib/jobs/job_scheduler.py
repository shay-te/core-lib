import logging
from threading import RLock, Timer
from pytimeparse import parse
from core_lib.jobs.job import Job


logger = logging.getLogger(__name__)


class JobScheduler(object):
    def __init__(self):
        self._lock = RLock() # RLock allows the same thread to acquire the lock again (prevents self-deadlock)
        self._job_to_timer = {}
        self._running_job_class_names = set()
        self._stopped_jobs = set()

    def stop(self, job: Job):
        # Cancel a pending timer AND mark the job stopped, so a recurring chain halts
        # even if stop() lands while the job is mid-run (cancel() is then a no-op).
        self._lock.acquire()
        self._stopped_jobs.add(job)
        timer = self._job_to_timer.get(job)
        if timer:
            timer.cancel()
        self._lock.release()

    def schedule(self, initial_delay: str, frequency: str, job: Job, is_run_in_parallel: bool = False):
        logger.info(f'schedule {job.__repr__() if job else "<None Job>"}, initial_delay: {initial_delay}, frequency: {frequency} ')
        self._validate(initial_delay, job)
        self._validate_str_time(frequency, 'frequency')
        self._reset_stopped(job)
        self._schedule(initial_delay, frequency, job, is_run_in_parallel)

    # One-shot jobs default to parallel: each is scheduled per-event (e.g. per delete),
    # so silently skipping an overlapping trigger would DROP the event. Only recurring
    # jobs default to no-parallel (skip-if-already-running).
    def schedule_once(self, initial_delay: str, job: Job, is_run_in_parallel: bool = True, params: dict = {}):
        logger.info(f'schedule_once {job.__repr__() if job else "<None Job>"}, initial_delay: {initial_delay}')
        self._validate(initial_delay, job)
        self._reset_stopped(job)
        self._schedule(initial_delay, None, job, is_run_in_parallel, params)

    def _reset_stopped(self, job: Job):
        self._lock.acquire()
        self._stopped_jobs.discard(job)
        self._lock.release()

    def _schedule(self, initial_delay: str, frequency: str, job: Job, is_run_in_parallel: bool = False, params: dict = {}):
        self._lock.acquire()
        timer = Timer(parse(initial_delay), self._run_job, kwargs={'job': job, 'frequency': frequency, 'is_run_in_parallel': is_run_in_parallel, 'params': params})
        timer.daemon = True
        self._job_to_timer[job] = timer
        timer.start()
        self._lock.release()

    def _run_job(self, job: Job, frequency: str, is_run_in_parallel: bool = False, params: dict = {}):
        # stop() may have landed after this timer fired — don't run, don't reschedule.
        self._lock.acquire()
        stopped = job in self._stopped_jobs
        self._lock.release()
        if stopped:
            self._job_to_timer.pop(job, None)
            return

        # When not running in parallel, a trigger that fires while another job of the
        # same class is still running is IGNORED (logged + rescheduled) — the running
        # job is never stopped.
        job_class_name = job.__class__.__name__
        if not is_run_in_parallel:
            self._lock.acquire()
            already_running = job_class_name in self._running_job_class_names
            if not already_running:
                self._running_job_class_names.add(job_class_name)
            self._lock.release()
            if already_running:
                logger.info(f'job `{job_class_name}` is already running, ignoring this run')
                self._job_to_timer.pop(job, None)
                if frequency:
                    self._schedule(frequency, frequency, job, is_run_in_parallel)
                return

        try:
            logger.debug(f'Running job {job.__repr__() if job else "<None Job>"}')
            job.run(**params)
        except BaseException as ex:
            logger.error(f'Error while running job {job.__repr__() if job else "<None Job>"}')
            logger.exception(ex, exc_info=True)

        if not is_run_in_parallel:
            self._lock.acquire()
            self._running_job_class_names.discard(job_class_name)
            self._lock.release()
        self._job_to_timer.pop(job, None)
        if frequency:
            self._schedule(frequency, frequency, job, is_run_in_parallel)

    def _validate(self, initial_delay: str, job: Job):
        assert job
        assert isinstance(job, Job)
        self._validate_str_time(initial_delay, 'initial_delay')

    def _validate_str_time(self, str_time: str, variable_name: str):
        error_msg = f'{variable_name} `{str_time}` is invalid'
        assert str_time, error_msg
        initial_delay_seconds = parse(str_time)
        assert initial_delay_seconds is not None, error_msg
