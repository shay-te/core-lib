import logging
from threading import RLock, Timer
from pytimeparse import parse
from core_lib.jobs.job import Job


logger = logging.getLogger(__name__)


class JobScheduler(object):
    def __init__(self):
        self._lock = RLock() # RLock allows the same thread to acquire the lock again (prevents self-deadlock)
        self._job_to_timer = {}
        self._job_class_name_to_job = {}

    def stop(self, job: Job):
        self._lock.acquire()
        timer = self._job_to_timer.get(job)
        if timer:
            timer.cancel()
        self._lock.release()

    def schedule(self, initial_delay: str, frequency: str, job: Job, is_run_in_parallel: bool = True):
        logger.info(f'schedule {job.__repr__() if job else "<None Job>"}, initial_delay: {initial_delay}, frequency: {frequency} ')
        self._validate(initial_delay, job)
        self._validate_str_time(frequency, 'frequency')
        self._schedule(initial_delay, frequency, job, is_run_in_parallel)

    def schedule_once(self, initial_delay: str, job: Job, is_run_in_parallel: bool = True, params: dict = {}):
        logger.info(f'schedule_once {job.__repr__() if job else "<None Job>"}, initial_delay: {initial_delay}')
        self._validate(initial_delay, job)
        self._schedule(initial_delay, None, job, is_run_in_parallel, params)

    def _schedule(self, initial_delay: str, frequency: str, job: Job, is_run_in_parallel: bool = True, params: dict = {}):
        self._lock.acquire()
        timer = Timer(parse(initial_delay), self._run_job, kwargs={'job': job, 'frequency': frequency, 'params': params})
        timer.daemon = True
        if not is_run_in_parallel:
            job_instance = self._job_class_name_to_job.get(job.__class__.__name__)
            if job_instance:
                self.stop(job_instance)
        self._job_to_timer[job] = timer
        self._job_class_name_to_job[job.__class__.__name__] = job
        timer.start()
        self._lock.release()

    def _run_job(self, job: Job, frequency: str, params: dict = {}):
        try:
            logger.debug(f'Running job {job.__repr__() if job else "<None Job>"}')
            job.run(**params)
        except BaseException as ex:
            logger.error(f'Error while running job {job.__repr__() if job else "<None Job>"}')
            logger.exception(ex, exc_info=True)

        del self._job_to_timer[job]
        if frequency:
            self._schedule(frequency, frequency, job)

    def _validate(self, initial_delay: str, job: Job):
        assert job
        assert isinstance(job, Job)
        self._validate_str_time(initial_delay, 'initial_delay')

    def _validate_str_time(self, str_time: str, variable_name: str):
        error_msg = f'{variable_name} `{str_time}` is invalid'
        assert str_time, error_msg
        initial_delay_seconds = parse(str_time)
        assert initial_delay_seconds is not None, error_msg
