import unittest
from datetime import timedelta
from time import sleep

from core_lib.helpers.thread import LockGroup


class TestThreadLockGroup(unittest.TestCase):

    def test_1(self):
        lock_group = LockGroup(timedelta(seconds=2))
        lock = lock_group.get_lock(1)
        self.assertEqual(len(lock_group.lock_dict), 1)
        lock_group.clear()
        self.assertEqual(len(lock_group.lock_dict), 1)
        sleep(3)
        lock_group.clear()
        self.assertEqual(len(lock_group.lock_dict), 0)
