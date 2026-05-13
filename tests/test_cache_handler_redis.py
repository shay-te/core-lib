import json
import unittest
from datetime import timedelta
from unittest.mock import MagicMock, patch

from core_lib.cache.cache_handler_redis import CacheHandlerRedis


class TestCacheHandlerRedis(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        patcher = patch('core_lib.cache.cache_handler_redis.redis.from_url', return_value=self.mock_client)
        self.addCleanup(patcher.stop)
        patcher.start()
        self.handler = CacheHandlerRedis('redis://localhost:6379')

    def test_get_returns_decoded_json(self):
        self.mock_client.get.return_value = json.dumps({'a': 1})
        self.assertEqual(self.handler.get('k'), {'a': 1})
        self.mock_client.get.assert_called_once_with('k')

    def test_get_none_when_missing(self):
        self.mock_client.get.return_value = None
        self.assertIsNone(self.handler.get('k'))

    def test_set_dict(self):
        self.handler.set('k', {'a': 1}, timedelta(seconds=30))
        self.mock_client.set.assert_called_once_with('k', json.dumps({'a': 1}), ex=timedelta(seconds=30))

    def test_set_list(self):
        self.handler.set('k', [1, 2, 3], timedelta(seconds=30))
        self.mock_client.set.assert_called_once_with('k', json.dumps([1, 2, 3]), ex=timedelta(seconds=30))

    def test_set_int(self):
        self.handler.set('k', 42, timedelta(seconds=30))
        self.mock_client.set.assert_called_once_with('k', json.dumps(42), ex=timedelta(seconds=30))

    def test_set_str(self):
        self.handler.set('k', 'val', timedelta(seconds=30))
        self.mock_client.set.assert_called_once_with('k', json.dumps('val'), ex=timedelta(seconds=30))

    def test_set_no_expire_uses_neg_one(self):
        self.handler.set('k', 'val', None)
        self.mock_client.set.assert_called_once_with('k', json.dumps('val'), ex=-1)

    def test_set_invalid_type_raises(self):
        with self.assertRaises(ValueError):
            self.handler.set('k', object(), timedelta(seconds=30))

    def test_delete(self):
        self.handler.delete('k')
        self.mock_client.delete.assert_called_once_with('k')

    def test_flush_all(self):
        self.handler.flush_all()
        self.mock_client.flushall.assert_called_once_with()
