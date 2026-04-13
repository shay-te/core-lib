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

    def test_is_run_in_parallel_false(self):
        scheduler = JobScheduler()
        job1 = TestJob()
        job2 = TestJob()

        scheduler.schedule('1s', '1s', job1, is_run_in_parallel=False)
        sleep(2)

        # scheduling another job of the same class should cancel the previous one
        scheduler.schedule('1s', '1s', job2, is_run_in_parallel=False)
        sleep(3)

        scheduler.stop(job1)
        scheduler.stop(job2)

        # job1 should have stopped when job2 was scheduled
        self.assertLess(job1.called, job2.called)
        self.assertGreater(job2.called, 0)

    def test_is_run_in_parallel_true(self):
        scheduler = JobScheduler()
        job1 = TestJob()
        job2 = TestJob()

        scheduler.schedule('1s', '1s', job1, is_run_in_parallel=True)
        scheduler.schedule('1s', '1s', job2, is_run_in_parallel=True)

        sleep(3.5)
        scheduler.stop(job1)
        scheduler.stop(job2)

        # both jobs should run independently
        self.assertGreater(job1.called, 0)
        self.assertGreater(job2.called, 0)

