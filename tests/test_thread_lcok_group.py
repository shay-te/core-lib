import unittest
from datetime import timedelta
from time import sleep

from freezegun import freeze_time

from core_lib.helpers.thread import LockGroup


class TestThreadLockGroup(unittest.TestCase):
    def test_1(self):
        lock_group = LockGroup(timedelta(seconds=2))
        lock_group.get_lock(1)
        self.assertEqual(len(lock_group.lock_dict), 1)
        lock_group.clear()
        self.assertEqual(len(lock_group.lock_dict), 1)
        sleep(3)
        lock_group.clear()
        self.assertEqual(len(lock_group.lock_dict), 0)

    def test_clear_keeps_held_lock(self):
        with freeze_time('2026-01-01 00:00:00') as frozen_time:
            lock_group = LockGroup(timedelta(seconds=2))
            held_lock = lock_group.get_lock('held')
            idle_lock = lock_group.get_lock('idle')
            held_lock.acquire()
            try:
                frozen_time.tick(timedelta(seconds=3))
                lock_group.clear()
                self.assertIs(lock_group.get_lock('held'), held_lock)
                self.assertIsNot(lock_group.get_lock('idle'), idle_lock)
            finally:
                held_lock.release()
