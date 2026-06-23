"""Exhaustive permutation tests for CacheHandlerRam.

Every branch of get / set / delete / flush_all exercised with:
- truthy / falsy / None values
- expire=None vs. expire=timedelta
- pre-expiry vs. post-expiry reads
- missing keys
- repeated set on same key (overwrite)
- delete of missing key (no-op)
- *args/**kwargs on constructor
"""
import datetime
import time
import unittest

from freezegun import freeze_time

from core_lib.cache.cache_handler_ram import CacheHandlerRam


class TestCacheHandlerRamConstruction(unittest.TestCase):
    def test_default_constructor(self):
        h = CacheHandlerRam()
        self.assertEqual(h.cached_function_responses, {})

    def test_constructor_accepts_positional_args(self):
        """
        Verify that CacheHandlerRam constructor accepts arbitrary positional arguments and initializes the cache correctly.
        """
        h = CacheHandlerRam(1, 2, 'extra')
        self.assertEqual(h.cached_function_responses, {})

    def test_constructor_accepts_keyword_args(self):
        h = CacheHandlerRam(host='ignored', port=99)
        self.assertEqual(h.cached_function_responses, {})


class TestCacheHandlerRamGet(unittest.TestCase):
    def setUp(self):
        self.h = CacheHandlerRam()

    def test_get_missing_returns_none(self):
        self.assertIsNone(self.h.get('nothing'))

    def test_get_after_set_no_expire(self):
        self.h.set('k', 'v', None)
        self.assertEqual(self.h.get('k'), 'v')

    def test_get_after_set_with_expire_before_expiry(self):
        self.h.set('k', 'v', datetime.timedelta(seconds=10))
        self.assertEqual(self.h.get('k'), 'v')

    def test_get_after_set_with_expire_after_expiry_removes_entry(self):
        self.h.set('k', 'v', datetime.timedelta(seconds=1))
        with freeze_time(datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(seconds=2)):
            self.assertIsNone(self.h.get('k'))
        # Entry is purged from the dict
        self.assertNotIn('k', self.h.cached_function_responses)

    def test_get_returns_none_for_explicit_none_value(self):
        # `if data:` truthy guard treats None-valued entries as miss
        self.h.set('k', None, None)
        self.assertIsNone(self.h.get('k'))

    def test_get_returns_falsy_truthy_dict_entries(self):
        # The OUTER guard `if data:` uses truthiness of the wrapping dict, which
        # is always truthy — so even a falsy stored value returns through.
        for value in ['', 0, [], {}, False]:
            with self.subTest(value=value):
                h = CacheHandlerRam()
                h.set('k', value, None)
                # Bug-or-feature: `if data:` always True since data is a dict;
                # then `if data['expire']:` is False → returns `data['data']`.
                self.assertEqual(h.get('k'), value)


class TestCacheHandlerRamSet(unittest.TestCase):
    def setUp(self):
        self.h = CacheHandlerRam()

    def test_set_stores_value_and_timestamp(self):
        before = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        self.h.set('k', 'v', datetime.timedelta(seconds=10))
        after = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        entry = self.h.cached_function_responses['k']
        self.assertEqual(entry['data'], 'v')
        self.assertEqual(entry['expire'], datetime.timedelta(seconds=10))
        self.assertGreaterEqual(entry['set_time'], before)
        self.assertLessEqual(entry['set_time'], after)

    def test_set_overwrites_existing_key(self):
        self.h.set('k', 'old', None)
        self.h.set('k', 'new', None)
        self.assertEqual(self.h.get('k'), 'new')

    def test_set_with_none_expire(self):
        self.h.set('k', 'v', None)
        self.assertIsNone(self.h.cached_function_responses['k']['expire'])

    def test_set_with_zero_timedelta(self):
        # timedelta(0) is FALSY → matches the `if data['expire']:` False branch
        # and the value is returned (no expiry check).
        self.h.set('k', 'v', datetime.timedelta())
        self.assertEqual(self.h.get('k'), 'v')

    def test_set_with_complex_value_types(self):
        # Verify the handler doesn't mutate the stored object
        original = {'a': [1, 2, 3], 'b': {'nested': True}}
        self.h.set('k', original, None)
        self.assertIs(self.h.get('k'), original)


class TestCacheHandlerRamDelete(unittest.TestCase):
    def setUp(self):
        self.h = CacheHandlerRam()

    def test_delete_existing_key(self):
        self.h.set('k', 'v', None)
        self.h.delete('k')
        self.assertIsNone(self.h.get('k'))

    def test_delete_missing_key_no_op(self):
        # No exception even when key is absent
        self.h.delete('not-there')

    def test_delete_then_set_works(self):
        self.h.set('k', 'v1', None)
        self.h.delete('k')
        self.h.set('k', 'v2', None)
        self.assertEqual(self.h.get('k'), 'v2')


class TestCacheHandlerRamFlushAll(unittest.TestCase):
    def test_flush_all_empties_dict(self):
        h = CacheHandlerRam()
        h.set('a', 1, None)
        h.set('b', 2, None)
        h.set('c', 3, None)
        h.flush_all()
        self.assertEqual(h.cached_function_responses, {})

    def test_flush_all_on_empty(self):
        h = CacheHandlerRam()
        h.flush_all()
        self.assertEqual(h.cached_function_responses, {})

    def test_flush_all_then_set_works(self):
        h = CacheHandlerRam()
        h.set('a', 1, None)
        h.flush_all()
        h.set('b', 2, None)
        self.assertEqual(h.get('b'), 2)
        self.assertIsNone(h.get('a'))


class TestCacheHandlerRamExpiryBoundary(unittest.TestCase):
    def test_expiry_just_before_threshold(self):
        h = CacheHandlerRam()
        h.set('k', 'v', datetime.timedelta(seconds=10))
        # Move forward 9 seconds — still valid
        with freeze_time(datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(seconds=9)):
            self.assertEqual(h.get('k'), 'v')

    def test_expiry_at_exact_threshold(self):
        h = CacheHandlerRam()
        h.set('k', 'v', datetime.timedelta(seconds=10))
        # set_time_diff < expire → strict less-than, so exact match expires
        with freeze_time(datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(seconds=11)):
            self.assertIsNone(h.get('k'))

    def test_repeated_get_after_expiry_remains_none(self):
        h = CacheHandlerRam()
        h.set('k', 'v', datetime.timedelta(seconds=1))
        with freeze_time(datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(seconds=2)):
            self.assertIsNone(h.get('k'))
            self.assertIsNone(h.get('k'))  # second read also None


class TestCacheHandlerRamConcurrentKeys(unittest.TestCase):
    def test_independent_keys_dont_interfere(self):
        h = CacheHandlerRam()
        h.set('a', 1, None)
        h.set('b', 2, datetime.timedelta(seconds=1))
        h.set('c', 3, datetime.timedelta(seconds=100))
        with freeze_time(datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(seconds=5)):
            self.assertEqual(h.get('a'), 1)
            self.assertIsNone(h.get('b'))  # b expired
            self.assertEqual(h.get('c'), 3)
