import threading
import unittest
from datetime import timedelta
from time import sleep

from core_lib.helpers.thread import LockGroup


class TestThreadLockGroup(unittest.TestCase):
    def test_basic_get_and_clear(self):
        lock_group = LockGroup(timedelta(seconds=2))
        lock_group.get_lock(1)
        self.assertEqual(len(lock_group.lock_dict), 1)
        lock_group.clear()
        self.assertEqual(len(lock_group.lock_dict), 1)
        sleep(3)
        lock_group.clear()
        self.assertEqual(len(lock_group.lock_dict), 0)

    def test_get_lock_returns_lock(self):
        group = LockGroup(timedelta(seconds=10))
        lock = group.get_lock('key')
        self.assertIsNotNone(lock)
        self.assertTrue(hasattr(lock, 'acquire'))

    def test_same_key_returns_same_lock(self):
        group = LockGroup(timedelta(seconds=10))
        lock1 = group.get_lock('key')
        lock2 = group.get_lock('key')
        self.assertIs(lock1, lock2)

    def test_different_keys_return_different_locks(self):
        group = LockGroup(timedelta(seconds=10))
        lock1 = group.get_lock('key1')
        lock2 = group.get_lock('key2')
        self.assertIsNot(lock1, lock2)

    def test_multiple_keys_tracked(self):
        group = LockGroup(timedelta(seconds=10))
        group.get_lock('a')
        group.get_lock('b')
        group.get_lock('c')
        self.assertEqual(len(group.lock_dict), 3)

    def test_integer_keys(self):
        group = LockGroup(timedelta(seconds=10))
        self.assertIs(group.get_lock(1), group.get_lock(1))

    def test_tuple_keys(self):
        group = LockGroup(timedelta(seconds=10))
        self.assertIsNotNone(group.get_lock(('user', 42)))

    def test_none_key(self):
        group = LockGroup(timedelta(seconds=10))
        self.assertIsNotNone(group.get_lock(None))

    def test_clear_does_not_remove_fresh_locks(self):
        group = LockGroup(timedelta(seconds=10))
        group.get_lock('key')
        group.clear()
        self.assertEqual(len(group.lock_dict), 1)

    def test_clear_removes_expired_locks(self):
        group = LockGroup(timedelta(milliseconds=50))
        group.get_lock('key')
        sleep(0.1)
        group.clear()
        self.assertEqual(len(group.lock_dict), 0)

    def test_clear_selective_removal(self):
        group = LockGroup(timedelta(milliseconds=50))
        group.get_lock('expires')
        sleep(0.1)
        group.get_lock('fresh')
        group.clear()
        self.assertNotIn('expires', group.lock_dict)
        self.assertIn('fresh', group.lock_dict)

    def test_clear_empty_group_no_error(self):
        group = LockGroup(timedelta(seconds=10))
        group.clear()
        self.assertEqual(len(group.lock_dict), 0)

    def test_accessing_key_after_expiry_recreates_lock(self):
        group = LockGroup(timedelta(milliseconds=50))
        lock1 = group.get_lock('key')
        sleep(0.1)
        group.clear()
        lock2 = group.get_lock('key')
        self.assertIsNot(lock1, lock2)

    def test_lock_actually_locks(self):
        group = LockGroup(timedelta(seconds=10))
        lock = group.get_lock('key')
        results = []

        def worker():
            with lock:
                results.append('start')
                sleep(0.05)
                results.append('end')

        t1 = threading.Thread(target=worker)
        t2 = threading.Thread(target=worker)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        self.assertEqual(results.count('start'), 2)
        self.assertEqual(results.count('end'), 2)
        self.assertEqual(results[0], 'start')
        self.assertEqual(results[1], 'end')

    def test_get_lock_thread_safe(self):
        group = LockGroup(timedelta(seconds=10))
        locks = []
        errors = []

        def get():
            try:
                locks.append(group.get_lock('shared'))
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=get) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0)
        self.assertEqual(len(locks), 20)
        first = locks[0]
        self.assertTrue(all(l is first for l in locks))

    def test_different_keys_dont_block_each_other(self):
        group = LockGroup(timedelta(seconds=10))
        results = []

        def hold_lock(key, delay):
            with group.get_lock(key):
                sleep(delay)
                results.append(key)

        t1 = threading.Thread(target=hold_lock, args=('a', 0.05))
        t2 = threading.Thread(target=hold_lock, args=('b', 0.05))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        self.assertIn('a', results)
        self.assertIn('b', results)
