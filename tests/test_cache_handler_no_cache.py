import datetime
import unittest

from core_lib.cache.cache_handler_no_cache import CacheHandlerNoCache


class TestCacheHandlerNoCache(unittest.TestCase):
    def setUp(self):
        self.handler = CacheHandlerNoCache()

    def test_get_returns_none(self):
        self.assertIsNone(self.handler.get('any_key'))

    def test_set_is_noop(self):
        self.assertIsNone(self.handler.set('key', 'value', datetime.timedelta(seconds=10)))

    def test_delete_is_noop(self):
        self.assertIsNone(self.handler.delete('key'))

    def test_flush_all_is_noop(self):
        self.assertIsNone(self.handler.flush_all())

    def test_cached_function_responses_dict_initialized(self):
        self.assertEqual(self.handler.cached_function_responses, {})
