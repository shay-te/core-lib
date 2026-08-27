import unittest
from datetime import timedelta, datetime

from freezegun import freeze_time

from core_lib.cache.cache_handler_ram import CacheHandlerRam


class TestCacheHandlerRam(unittest.TestCase):
    def setUp(self):
        self.cache = CacheHandlerRam()

    def test_set_and_get(self):
        self.cache.set('key', 'value', timedelta(seconds=10))
        self.assertEqual(self.cache.get('key'), 'value')

    def test_get_missing_key_returns_none(self):
        self.assertIsNone(self.cache.get('missing'))

    def test_expired_entry_returns_none(self):
        self.cache.set('key', 'value', timedelta(seconds=5))
        with freeze_time(datetime.utcnow() + timedelta(seconds=6)):
            self.assertIsNone(self.cache.get('key'))

    def test_unexpired_entry_is_returned(self):
        self.cache.set('key', 'value', timedelta(seconds=10))
        with freeze_time(datetime.utcnow() + timedelta(seconds=9)):
            self.assertEqual(self.cache.get('key'), 'value')

    def test_no_expiry_persists(self):
        self.cache.set('key', 'value', None)
        with freeze_time(datetime.utcnow() + timedelta(days=365)):
            self.assertEqual(self.cache.get('key'), 'value')

    def test_expired_entry_removed_from_store(self):
        self.cache.set('key', 'value', timedelta(seconds=5))
        with freeze_time(datetime.utcnow() + timedelta(seconds=6)):
            self.cache.get('key')
        self.assertNotIn('key', self.cache.cached_function_responses)

    def test_delete_removes_entry(self):
        self.cache.set('key', 'value', timedelta(seconds=10))
        self.cache.delete('key')
        self.assertIsNone(self.cache.get('key'))

    def test_delete_missing_key_no_error(self):
        self.cache.delete('nonexistent')

    def test_flush_all_clears_everything(self):
        self.cache.set('k1', 'v1', timedelta(seconds=10))
        self.cache.set('k2', 'v2', timedelta(seconds=10))
        self.cache.flush_all()
        self.assertIsNone(self.cache.get('k1'))
        self.assertIsNone(self.cache.get('k2'))
        self.assertEqual(len(self.cache.cached_function_responses), 0)

    def test_set_overwrites_existing(self):
        self.cache.set('key', 'old', timedelta(seconds=10))
        self.cache.set('key', 'new', timedelta(seconds=10))
        self.assertEqual(self.cache.get('key'), 'new')

    def test_stores_various_types(self):
        cases = [42, 3.14, [1, 2], {'a': 1}, (1,), True]
        for value in cases:
            self.cache.set('key', value, timedelta(seconds=10))
            self.assertEqual(self.cache.get('key'), value)

    def test_independent_keys(self):
        self.cache.set('a', 1, timedelta(seconds=10))
        self.cache.set('b', 2, timedelta(seconds=10))
        self.assertEqual(self.cache.get('a'), 1)
        self.assertEqual(self.cache.get('b'), 2)
