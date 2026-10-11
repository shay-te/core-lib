"""CacheHandlerRedis sends SET with EX only when an expire is given, so @Cache without expire works on Redis."""
import json
import unittest
from datetime import timedelta

from core_lib.cache.cache_handler_redis import CacheHandlerRedis


class TestCacheHandlerRedis(unittest.TestCase):

    def setUp(self):
        # No server: the client connects lazily, and the test records the command
        # redis-py would send at its outbound boundary, execute_command().
        self.cache_handler = CacheHandlerRedis('redis://127.0.0.1:6379/0')
        self.sent_commands = []
        self.cache_handler.redis_client.execute_command = self._record_command

    def _record_command(self, *args, **options):
        self.sent_commands.append(args)
        return True

    def test_set_without_expire_sends_no_ex(self):
        self.cache_handler.set('acme_widget_1', {'name': 'widget'}, None)

        self.assertEqual([('SET', 'acme_widget_1', json.dumps({'name': 'widget'}))], self.sent_commands)

    def test_set_with_expire_sends_ex_in_seconds(self):
        self.cache_handler.set('acme_widget_1', [1, 2], timedelta(minutes=10))

        self.assertEqual([('SET', 'acme_widget_1', json.dumps([1, 2]), 'EX', 600)], self.sent_commands)

    def test_set_rejects_a_type_json_cannot_round_trip(self):
        with self.assertRaises(ValueError):
            self.cache_handler.set('acme_widget_1', 1.5, None)
        self.assertEqual([], self.sent_commands)
