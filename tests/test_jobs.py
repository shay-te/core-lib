import threading
import unittest
from time import sleep

from core_lib.jobs.job import Job
from core_lib.jobs.job_scheduler import JobScheduler


class TestJob(Job):
    def __init__(self):
        self.called = 0

    def initialized(self, data_handler):
        pass

    def run(self):
        self.called = self.called + 1


class TestJobRaiseException(Job):
    called = 0

    def initialized(self, data_handler):
        pass

    def run(self):
        if TestJobRaiseException.called == 3:
            raise BaseException
        TestJobRaiseException.called = TestJobRaiseException.called + 1

class TestJobWithParams(Job):
    def __init__(self):
        self.received = None

    def initialized(self, data_handler):
        pass

    def run(self, **params):
        self.received = params


class SlowJob(Job):
    def __init__(self, run_seconds: float = 2):
        self.called = 0
        self.run_seconds = run_seconds

    def initialized(self, data_handler):
        pass

    def run(self):
        sleep(self.run_seconds)
        self.called = self.called + 1


class OtherClassJob(Job):
    def __init__(self):
        self.called = 0

    def initialized(self, data_handler):
        pass

    def run(self):
        self.called = self.called + 1


class AlwaysFailJob(Job):
    def __init__(self):
        self.attempts = 0

    def initialized(self, data_handler):
        pass

    def run(self):
        self.attempts = self.attempts + 1
        raise ValueError('boom')


class ConcurrencyTrackingJob(Job):
    # Class-level counters shared by all instances — proves whether two runs of the
    # same class ever execute at the same moment.
    current = 0
    max_concurrent = 0
    _track_lock = threading.Lock()

    def __init__(self, run_seconds: float = 1.5):
        self.called = 0
        self.run_seconds = run_seconds

    @classmethod
    def reset(cls):
        cls.current = 0
        cls.max_concurrent = 0

    def initialized(self, data_handler):
        pass

    def run(self):
        with ConcurrencyTrackingJob._track_lock:
            ConcurrencyTrackingJob.current += 1
            ConcurrencyTrackingJob.max_concurrent = max(
                ConcurrencyTrackingJob.max_concurrent, ConcurrencyTrackingJob.current
            )
        sleep(self.run_seconds)
        with ConcurrencyTrackingJob._track_lock:
            ConcurrencyTrackingJob.current -= 1
        self.called = self.called + 1


class TestJobs(unittest.TestCase):
    def test_job_decorator(self):
        j = TestJob()
        j.run()
        self.assertEqual(j.called, 1)

    def test_schedule_invalid(self):
        scheduler = JobScheduler()
        job = TestJob()
        self.assertRaises(AssertionError, scheduler.schedule_once, 'asd;lasdfj', job)
        self.assertRaises(AssertionError, scheduler.schedule_once, None, job)
        self.assertRaises(AssertionError, scheduler.schedule_once, '1s', None)
        self.assertRaises(AssertionError, scheduler.schedule_once, '1s', 'not a job')

        self.assertRaises(AssertionError, scheduler.schedule, '1s', None, job)
        self.assertRaises(AssertionError, scheduler.schedule, '1s', 'asdasdasd', job)
        self.assertRaises(AssertionError, scheduler.schedule, '1s', '2s', None)
        self.assertRaises(AssertionError, scheduler.schedule, '1s', '2s', 'not a job')

    def test_schedule(self):
        scheduler = JobScheduler()
        job = TestJob()
        scheduler.schedule_once('1s', job)
        sleep(2)
        self.assertEqual(job.called, 1)

        scheduler.schedule('1s', '1s', job)
        sleep(5)
        scheduler.stop(job)
        last_value = job.called
        sleep(5)
        self.assertEqual(job.called, last_value)
        self.assertGreater(job.called, 2)

    def test_schedule_log(self):
        scheduler = JobScheduler()
        job_exception = TestJobRaiseException()
        with self.assertLogs() as cm:
            scheduler.schedule('1s', '1s', job_exception)
            sleep(10.1)
            scheduler.stop(job_exception)
            log = str(cm.output)
            self.assertIn('BaseException', log)
            self.assertIn('Error while running job', log)

    def test_schedule_once_with_params(self):
        scheduler = JobScheduler()
        job = TestJobWithParams()

        scheduler.schedule_once('1s', job, params={'a': 1, 'b': 'test'})
        sleep(2)

        self.assertEqual(job.received, {'a': 1, 'b': 'test'})

    def test_default_parallelism(self):
        import inspect
        # recurring jobs default to no-parallel (skip-if-already-running)
        self.assertIs(inspect.signature(JobScheduler.schedule).parameters['is_run_in_parallel'].default, False)
        # one-shot jobs default to PARALLEL — each is scheduled per-event, so skipping
        # an overlap would drop the event
        self.assertIs(inspect.signature(JobScheduler.schedule_once).parameters['is_run_in_parallel'].default, True)

    def test_schedule_once_defaults_to_parallel_never_drops_events(self):
        # Two same-class one-shots scheduled per-event must BOTH run by default.
        ConcurrencyTrackingJob.reset()
        scheduler = JobScheduler()
        job1 = ConcurrencyTrackingJob(1.5)
        job2 = ConcurrencyTrackingJob(1.5)
        scheduler.schedule_once('1s', job1)
        scheduler.schedule_once('1s', job2)
        sleep(4)
        self.assertEqual(job1.called, 1)
        self.assertEqual(job2.called, 1)

    def test_is_run_in_parallel_false(self):
        # With is_run_in_parallel=False an overlapping trigger of the SAME class is
        # ignored, and the running job is never stopped.
        scheduler = JobScheduler()
        job1 = SlowJob(2)
        job2 = SlowJob(2)

        # job1 starts at ~1s and runs for 2s
        scheduler.schedule_once('1s', job1, is_run_in_parallel=False)
        # job2 (same class) fires at ~2s while job1 is still running -> ignored
        scheduler.schedule_once('2s', job2, is_run_in_parallel=False)
        sleep(4.5)

        self.assertEqual(job1.called, 1)  # the running job completed, never stopped
        self.assertEqual(job2.called, 0)  # the overlapping one-shot was ignored

        # once the class is free again, new triggers run normally
        scheduler.schedule_once('1s', job2, is_run_in_parallel=False)
        sleep(3.5)
        self.assertEqual(job2.called, 1)

    def test_skipped_recurring_trigger_retries_until_class_is_free(self):
        # A recurring job whose triggers fire while another same-class job is running
        # keeps RETRYING on its own frequency (the chain never dies) and runs once
        # the class frees up.
        scheduler = JobScheduler()
        blocker = SlowJob(3)
        recurring = SlowJob(0.1)

        scheduler.schedule_once('1s', blocker, is_run_in_parallel=False)  # busy ~1s..4s
        scheduler.schedule('2s', '1s', recurring)   # fires ~2s,3s (skipped), runs after ~4s
        sleep(6.5)
        scheduler.stop(recurring)

        self.assertEqual(blocker.called, 1)          # blocker was never stopped
        self.assertGreaterEqual(recurring.called, 1) # skipped chain survived and ran

    def test_different_classes_run_in_parallel(self):
        # The no-parallel guard is keyed by class name — a job of ANOTHER class runs
        # immediately even while the first is busy.
        scheduler = JobScheduler()
        slow = SlowJob(2)
        other = OtherClassJob()

        scheduler.schedule_once('1s', slow, is_run_in_parallel=False)    # busy ~1s..3s
        scheduler.schedule_once('2s', other, is_run_in_parallel=False)   # fires at ~2s, different class
        sleep(2.7)

        self.assertEqual(other.called, 1)  # ran DURING slow's run
        self.assertEqual(slow.called, 0)   # slow still running at this point
        sleep(1)
        self.assertEqual(slow.called, 1)

    def test_is_run_in_parallel_true_allows_same_class_overlap(self):
        # Explicit opt-in keeps the old behavior: same-class jobs run side by side.
        ConcurrencyTrackingJob.reset()
        scheduler = JobScheduler()
        job1 = ConcurrencyTrackingJob(2)
        job2 = ConcurrencyTrackingJob(2)

        scheduler.schedule_once('1s', job1, is_run_in_parallel=True)
        scheduler.schedule_once('1s', job2, is_run_in_parallel=True)
        sleep(4.5)

        self.assertEqual(job1.called, 1)
        self.assertEqual(job2.called, 1)
        self.assertGreaterEqual(ConcurrencyTrackingJob.max_concurrent, 2)

    def test_recurring_job_never_overlaps_itself(self):
        # frequency counts from COMPLETION — a recurring job can never overlap itself,
        # and with the default false the class never runs twice at the same moment.
        ConcurrencyTrackingJob.reset()
        scheduler = JobScheduler()
        job = ConcurrencyTrackingJob(1.5)

        scheduler.schedule('1s', '1s', job)
        sleep(7)
        scheduler.stop(job)
        sleep(2)

        self.assertGreaterEqual(job.called, 2)
        self.assertEqual(ConcurrencyTrackingJob.max_concurrent, 1)

    def test_exception_releases_the_running_marker(self):
        # A job that raises must release the running marker — the next same-class
        # trigger runs instead of being ignored forever.
        scheduler = JobScheduler()
        job1 = AlwaysFailJob()
        job2 = AlwaysFailJob()

        scheduler.schedule_once('1s', job1, is_run_in_parallel=False)
        sleep(2.2)
        self.assertEqual(job1.attempts, 1)

        scheduler.schedule_once('1s', job2, is_run_in_parallel=False)
        sleep(2.2)
        self.assertEqual(job2.attempts, 1)  # ran (marker was released), not skipped

    def test_stop_halts_chain_when_called_mid_run(self):
        # stop() landing while the job is running must still halt the chain — no
        # further runs after the in-progress one completes.
        scheduler = JobScheduler()
        job = SlowJob(2)
        scheduler.schedule('0s', '1s', job)  # starts immediately, runs 2s
        sleep(1)                             # stop lands mid-run
        scheduler.stop(job)
        sleep(4)
        self.assertEqual(job.called, 1)      # only the in-progress run; no reschedule

    def test_two_recurring_same_class_chains_both_survive(self):
        # Two recurring jobs of the same class: their triggers collide and skip, but
        # BOTH chains keep retrying and both make progress (no chain ever dies).
        scheduler = JobScheduler()
        job_a = SlowJob(1)
        job_b = SlowJob(1)

        scheduler.schedule('1s', '1s', job_a)
        scheduler.schedule('1s', '1s', job_b)
        sleep(8)
        scheduler.stop(job_a)
        scheduler.stop(job_b)
        sleep(2)

        self.assertGreaterEqual(job_a.called, 1)
        self.assertGreaterEqual(job_b.called, 1)
