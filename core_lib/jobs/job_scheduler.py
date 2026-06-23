import logging
from threading import RLock, Timer
from typing import Optional
from pytimeparse import parse
from core_lib.jobs.job import Job


logger = logging.getLogger(__name__)


class JobScheduler(object):
    def __init__(self):
        """
        Initialize the job scheduler with thread-safe state management.
        """
        self._lock = RLock() # RLock allows the same thread to acquire the lock again (prevents self-deadlock)
        self._job_to_timer = {}
        self._job_class_name_to_job = {}

    def stop(self, job: Job):
        # Use a context manager so the lock is released even if cancel raises.
        # Previous implementation called release() unguarded → deadlock on
        # exception.
        """
        Cancel the scheduled timer for a job.
        """
        with self._lock:
            timer = self._job_to_timer.get(job)
            if timer:
                timer.cancel()

    def schedule(self, initial_delay: str, frequency: str, job: Job, is_run_in_parallel: bool = True):
        """
        Schedule a job to run after an initial delay and repeat at a specified frequency.
        """
        logger.info(f'schedule {job.__repr__() if job else "<None Job>"}, initial_delay: {initial_delay}, frequency: {frequency} ')
        self._validate(initial_delay, job)
        self._validate_str_time(frequency, 'frequency')
        self._schedule(initial_delay, frequency, job, is_run_in_parallel)

    def schedule_once(self, initial_delay: str, job: Job, is_run_in_parallel: bool = True, params: Optional[dict] = None):
        """
        Schedule a job to run once after a specified delay.
        
        Parameters:
        	initial_delay (str): Time delay string (e.g., "5s", "1m")
        	params (Optional[dict]): Parameters to pass to the job's run method
        """
        logger.info(f'schedule_once {job.__repr__() if job else "<None Job>"}, initial_delay: {initial_delay}')
        self._validate(initial_delay, job)
        self._schedule(initial_delay, None, job, is_run_in_parallel, params)

    def _schedule(self, initial_delay: str, frequency: Optional[str], job: Job, is_run_in_parallel: bool = True, params: Optional[dict] = None):
        # `params=None` then resolved internally — avoids the classic
        # "shared mutable default" bug (every caller seeing the same dict).
        """
        Schedule a job to run after an initial delay, with optional rescheduling and sequential execution per job class.
        
        Sets up a Timer to execute the job after the delay specified by initial_delay. If frequency is provided, the job will be rescheduled to run repeatedly at that frequency. When is_run_in_parallel is False, any previously scheduled job of the same class is stopped before scheduling this one, ensuring sequential execution for that class.
        
        Parameters:
        	initial_delay (str): Time delay before first execution (e.g., '5s', '2m').
        	frequency (Optional[str]): Time interval for rescheduling; if None, the job runs once only.
        	job (Job): The job instance to schedule.
        	is_run_in_parallel (bool): If False, stops the last scheduled job of the same class to prevent concurrent execution. Defaults to True.
        	params (Optional[dict]): Keyword arguments to pass to the job's run method. Defaults to None, treated as an empty dict.
        """
        if params is None:
            params = {}
        with self._lock:
            timer = Timer(parse(initial_delay), self._run_job, kwargs={'job': job, 'frequency': frequency, 'params': params})
            timer.daemon = True
            if not is_run_in_parallel:
                job_instance = self._job_class_name_to_job.get(job.__class__.__name__)
                if job_instance:
                    self.stop(job_instance)
            self._job_to_timer[job] = timer
            self._job_class_name_to_job[job.__class__.__name__] = job
            timer.start()

    def _run_job(self, job: Job, frequency: Optional[str], params: Optional[dict] = None):
        """
        Execute a scheduled job and optionally reschedule it based on the specified frequency.
        """
        if params is None:
            params = {}
        try:
            logger.debug(f'Running job {job.__repr__() if job else "<None Job>"}')
            job.run(**params)
        # Catch Exception only — a job's bug should not also swallow
        # KeyboardInterrupt / SystemExit on the timer thread.
        except Exception as ex:
            logger.error(f'Error while running job {job.__repr__() if job else "<None Job>"}')
            logger.exception(ex, exc_info=True)

        # Guard the shared dict access with the lock — _run_job runs on the
        # Timer thread and races against schedule/stop on the main thread.
        # Use pop(...,  None) so a concurrent stop()->del doesn't KeyError.
        with self._lock:
            self._job_to_timer.pop(job, None)
        if frequency:
            self._schedule(frequency, frequency, job)

    def _validate(self, initial_delay: str, job: Job):
        # Explicit raises so `python -O` doesn't strip the validation.
        """
        Validates the job instance and initial delay string.
        
        Raises:
            AssertionError: If the job is None, not an instance of Job, or if the initial delay string is invalid.
        """
        if not job:
            raise AssertionError('JobScheduler: job cannot be None')
        if not isinstance(job, Job):
            raise AssertionError(
                f'JobScheduler: job must be an instance of Job, got {type(job).__name__}'
            )
        self._validate_str_time(initial_delay, 'initial_delay')

    def _validate_str_time(self, str_time: str, variable_name: str):
        """
        Validate that a time string represents a valid time interval.
        
        Parameters:
            variable_name (str): The variable name to include in the error message if validation fails
        
        Raises:
            AssertionError: If the time string is empty or cannot be parsed as a valid time interval
        """
        error_msg = f'{variable_name} `{str_time}` is invalid'
        if not str_time:
            raise AssertionError(error_msg)
        initial_delay_seconds = parse(str_time)
        if initial_delay_seconds is None:
            raise AssertionError(error_msg)
