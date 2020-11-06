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


class TestJobs(unittest.TestCase):

    def test_job_decorator(self):
        j = TestJob()
        j.run()
        self.assertEquals(j.called, 1)

    def test_schedule_invalid(self):
        s = JobScheduler()
        j = TestJob()
        self.assertRaises(AssertionError, s.schedule_once, 'asd;lasdfj', j)
        self.assertRaises(AssertionError, s.schedule_once, None, j)
        self.assertRaises(AssertionError, s.schedule_once, '1s', None)
        self.assertRaises(AssertionError, s.schedule_once, '1s', 'not a job')

        self.assertRaises(AssertionError, s.schedule, '1s', None, j)
        self.assertRaises(AssertionError, s.schedule, '1s', 'asdasdasd', j)
        self.assertRaises(AssertionError, s.schedule, '1s', '2s', None)
        self.assertRaises(AssertionError, s.schedule, '1s', '2s', 'not a job')

    def test_schedule(self):
        s = JobScheduler()
        j = TestJob()
        s.schedule_once('1s', j)
        sleep(2)
        self.assertEquals(j.called, 1)

        s.schedule('1s', '1s', j)
        sleep(5)
        s.stop(j)
        self.assertGreater(j.called, 2)


