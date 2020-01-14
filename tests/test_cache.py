import unittest
from datetime import timedelta
from time import sleep

from core_lib.cache.cache_ram import CacheRam


class CacheTest(unittest.TestCase):

    test_value = 100

    def test_cash(self):
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


    @CacheRam(key="test_cache_1", expire=timedelta(seconds=2))
    def get_cache(self):
        return CacheTest.test_value

    @CacheRam(key="test_cache_1", invalidate=True)
    def clear_cache(self):
        print("clean cache called")

    @CacheRam(key="test_cache_param_{param_1}", expire=timedelta(seconds=2))
    def get_cache_with_param(self, param_1):
        return CacheTest.test_value

    @CacheRam(key="test_cache_param_{param_1}", invalidate=True)
    def clear_cache_with_param(self, param_1):
        print("clean cache called")
