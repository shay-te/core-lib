import datetime
import json
import unittest
from unittest.mock import MagicMock, patch

from core_lib.cache.cache_handler_memcached import CacheHandlerMemcached


class TestCacheHandlerMemcached(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        patcher = patch(
            'core_lib.cache.cache_handler_memcached.Client', return_value=self.mock_client
        )
        self.addCleanup(patcher.stop)
        self.mock_client_class = patcher.start()
        self.handler = CacheHandlerMemcached('localhost:11211')

    def test_constructor_passes_url(self):
        self.mock_client_class.assert_called_once_with(['localhost:11211'])

    def test_get_returns_decoded_json(self):
        self.mock_client.get.return_value = json.dumps({'a': 1})
        self.assertEqual(self.handler.get('k'), {'a': 1})

    def test_get_none_when_missing(self):
        self.mock_client.get.return_value = None
        self.assertIsNone(self.handler.get('k'))

    def test_set_dict_with_expire(self):
        self.handler.set('k', {'a': 1}, datetime.timedelta(seconds=30))
        self.mock_client.set.assert_called_once_with('k', json.dumps({'a': 1}), time=30.0)

    def test_set_list_with_expire(self):
        self.handler.set('k', [1, 2], datetime.timedelta(seconds=10))
        self.mock_client.set.assert_called_once_with('k', json.dumps([1, 2]), time=10.0)

    def test_set_int_no_expire(self):
        self.handler.set('k', 5, None)
        self.mock_client.set.assert_called_once_with('k', json.dumps(5), time=0)

    def test_set_invalid_type_raises(self):
        with self.assertRaises(ValueError):
            self.handler.set('k', object(), datetime.timedelta(seconds=10))

    def test_delete(self):
        self.handler.delete('k')
        self.mock_client.delete.assert_called_once_with('k')

    def test_flush_all(self):
        self.handler.flush_all()
        self.mock_client.flush_all.assert_called_once_with()
