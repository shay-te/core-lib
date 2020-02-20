import unittest
from datetime import timedelta
from time import sleep

from core_lib.cache.cache import Cache
from core_lib.cache.cache_client_factory import CacheClientFactory
from core_lib.cache.cache_client_ram import CacheClientRam

cache_client_name = "xyz"
cache_factory = CacheClientFactory()
cache_factory.register(cache_client_name, CacheClientRam())
Cache.set_cache_factory(cache_factory)


class CacheTest(unittest.TestCase):

    test_value = 100

    def test_cache_client_register(self):
        self.assertRaises(ValueError, self.not_exists_cache_client_name)

    def test_cash(self):
        CacheTest.test_value = 100

        self.assertEqual(self.get_cache(), 100)
        CacheTest.test_value = 200
        self.assertEqual(self.get_cache(), 100)
        sleep(2.3)
        self.assertEqual(self.get_cache(), 200)
        CacheTest.test_value = 100
        self.assertEqual(self.get_cache(), 200)
        self.clear_cache()
        self.assertEqual(self.get_cache(), 100)

    def test_cash_with_param(self):
        CacheTest.test_value = 100

        param = "some_val"
        self.assertEqual(self.get_cache_with_param(param), 100)
        CacheTest.test_value = 200
        self.assertEqual(self.get_cache_with_param(param), 100)
        sleep(2.3)
        self.assertEqual(self.get_cache_with_param(param), 200)
        CacheTest.test_value = 100
        self.assertEqual(self.get_cache_with_param("other_param"), 100)
        self.assertEqual(self.get_cache_with_param(param), 200)
        self.clear_cache_with_param(param)
        self.assertEqual(self.get_cache_with_param(param), 100)

    def test_cash_with_param_optional(self):
        CacheTest.test_value = 100

        param = "some_val"
        self.assertEqual(self.get_cache_with_param_optional(param), 100)
        CacheTest.test_value = 200
        self.assertEqual(self.get_cache_with_param_optional(param), 100)
        sleep(2.3)
        self.assertEqual(self.get_cache_with_param_optional(param), 200)
        CacheTest.test_value = 100
        self.assertEqual(self.get_cache_with_param_optional("other_param"), 100)
        self.assertEqual(self.get_cache_with_param_optional(param), 200)
        self.clear_cache_with_param_optional(param)
        self.assertEqual(self.get_cache_with_param_optional(param), 100)

        self.assertEqual(self.get_cache_with_param_optional(param), 100)

        CacheTest.test_value = 400
        self.assertEqual(self.get_cache_with_param_optional(param, 3, 4, "param_4_new"), 400)

        CacheTest.test_value = 500
        self.assertEqual(self.get_cache_with_param_optional(param, 4), 500)

        CacheTest.test_value = 600
        self.assertEqual(self.get_cache_with_param_optional(param, 4, 5), 600)

        CacheTest.test_value = 700
        self.assertEqual(self.get_cache_with_param_optional(param, 4, 5, "__1"), 700)

        CacheTest.test_value = 800
        self.assertEqual(self.get_cache_with_param_optional(param, 4, 5, "__2"), 800)

    @Cache(key="test_cache_1", expire=timedelta(seconds=2))
    def get_cache(self):
        return CacheTest.test_value

    @Cache(key="test_cache_1", invalidate=True)
    def clear_cache(self):
        print("clean cache called")

    @Cache(key="test_cache_param_{param_1}", expire=timedelta(seconds=2), cache_client_name=cache_client_name)
    def get_cache_with_param(self, param_1):
        return CacheTest.test_value

    @Cache(key="test_cache_param_{param_1}", invalidate=True)
    def clear_cache_with_param(self, param_1):
        print("clean cache called")

    @Cache(key="test_cache_param_{param_1}{param_2}{param_3}{param_4}", expire=timedelta(seconds=2))
    def get_cache_with_param_optional(self, param_1, param_2=2, param_3=None, param_4="param4"):
        return CacheTest.test_value

    @Cache(key="test_cache_param_{param_1}{param_2}{param_3}{param_4}", invalidate=True, cache_client_name=cache_client_name)
    def clear_cache_with_param_optional(self, param_1, param_2=2, param_3=None, param_4="param4"):
        print("clean cache called")

    @Cache(key="test_cache_1", expire=timedelta(seconds=2), cache_client_name="sosososos")
    def not_exists_cache_client_name(self):
        return CacheTest.test_value