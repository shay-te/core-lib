"""CacheHandlerNoCache stores nothing: registered from config under a handler name, it turns @Cache off for every
method that names that handler, so each call runs the method."""
import unittest
from datetime import timedelta

from omegaconf import OmegaConf

from core_lib.cache.cache_decorator import Cache
from core_lib.cache.cache_handler_no_cache import CacheHandlerNoCache
from core_lib.core_lib import CoreLib
from core_lib.helpers.config_instances import instantiate_config

NO_CACHE_HANDLER = 'acme_no_cache'
CACHE_KEY_WIDGET = 'acme_widget_{widget_id}'


class WidgetReader(object):
    def __init__(self):
        self.calls = 0

    @Cache(CACHE_KEY_WIDGET, expire=timedelta(hours=1), handler_name=NO_CACHE_HANDLER)
    def get(self, widget_id: int):
        self.calls = self.calls + 1
        return {'widget_id': widget_id, 'calls': self.calls}

    @Cache(CACHE_KEY_WIDGET, invalidate=True, handler_name=NO_CACHE_HANDLER)
    def update(self, widget_id: int):
        pass


class TestCacheHandlerNoCache(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cache_handler = instantiate_config(
            OmegaConf.create({'_target_': 'core_lib.cache.cache_handler_no_cache.CacheHandlerNoCache'})
        )
        CoreLib.cache_registry.register(NO_CACHE_HANDLER, cache_handler)

    @classmethod
    def tearDownClass(cls):
        CoreLib.cache_registry.unregister(NO_CACHE_HANDLER)

    def test_every_call_runs_the_method(self):
        widget_reader = WidgetReader()

        self.assertEqual({'widget_id': 1, 'calls': 1}, widget_reader.get(1))
        self.assertEqual({'widget_id': 1, 'calls': 2}, widget_reader.get(1))
        widget_reader.update(1)  # invalidating a key that was never stored is not an error
        self.assertEqual({'widget_id': 1, 'calls': 3}, widget_reader.get(1))

    def test_set_stores_nothing_and_delete_and_flush_all_are_harmless(self):
        cache_handler = CacheHandlerNoCache()

        cache_handler.set('acme_widget_1', {'name': 'widget'}, timedelta(hours=1))
        self.assertIsNone(cache_handler.get('acme_widget_1'))

        cache_handler.delete('acme_widget_1')
        cache_handler.flush_all()
        self.assertIsNone(cache_handler.get('acme_widget_1'))
