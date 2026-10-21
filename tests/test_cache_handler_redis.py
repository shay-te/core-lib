"""CacheHandlerRedis against an in-memory Redis server (fakeredis): values round-trip as JSON, and a key set
without expire has no TTL, so @Cache without expire works on Redis."""
import unittest
from datetime import timedelta

import fakeredis

from core_lib.cache.cache_handler_redis import CacheHandlerRedis


class TestCacheHandlerRedis(unittest.TestCase):

    def setUp(self):
        self.cache_handler = CacheHandlerRedis('redis://127.0.0.1:6379/0')
        # The client the URL built connects lazily; an in-memory server takes its place before any command.
        self.redis_server = fakeredis.FakeRedis()
        self.cache_handler.redis_client = self.redis_server

    def test_set_without_expire_stores_the_key_with_no_ttl(self):
        self.cache_handler.set('acme_widget_1', {'name': 'widget'}, None)

        self.assertEqual(-1, self.redis_server.ttl('acme_widget_1'))
        self.assertEqual({'name': 'widget'}, self.cache_handler.get('acme_widget_1'))

    def test_set_with_expire_stores_the_ttl_in_seconds(self):
        self.cache_handler.set('acme_widget_1', [1, 2], timedelta(minutes=10))

        self.assertIn(self.redis_server.ttl('acme_widget_1'), (599, 600))
        self.assertEqual([1, 2], self.cache_handler.get('acme_widget_1'))

    def test_get_absent_key_is_none(self):
        self.assertIsNone(self.cache_handler.get('acme_widget_absent'))

    def test_set_rejects_a_type_json_cannot_round_trip(self):
        with self.assertRaises(ValueError):
            self.cache_handler.set('acme_widget_1', 1.5, None)
        self.assertIsNone(self.redis_server.get('acme_widget_1'))

    def test_delete_and_flush_all(self):
        self.cache_handler.set('acme_widget_1', 'one', None)
        self.cache_handler.set('acme_widget_2', 'two', None)

        self.cache_handler.delete('acme_widget_1')
        self.assertIsNone(self.cache_handler.get('acme_widget_1'))
        self.assertEqual('two', self.cache_handler.get('acme_widget_2'))

        self.cache_handler.flush_all()
        self.assertEqual([], self.redis_server.keys())
