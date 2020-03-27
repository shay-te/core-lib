import unittest
from datetime import timedelta
from time import sleep

from core_lib.cache.cache_decorator import Cache
from core_lib.cache.cache_client_ram import CacheClientRam
from core_lib.cache.cache_key_generator import CacheKeyGenerator
from core_lib.cache.default_cache_factory import DefaultCacheFactory

cache_client_name = "xyz"


class TestCache(unittest.TestCase):

    test_value = 100

    @classmethod
    def setUpClass(cls):
        cache_factory = DefaultCacheFactory()
        cache_factory.register(cache_client_name, CacheClientRam())
        Cache.set_factory(cache_factory)

    def test_cache_generates_key(self):
        def boo(param_1, param_2):
            return 1

        limit_key_length = 10
        cache_key_gen = CacheKeyGenerator(max_key_length=limit_key_length)
        key1 = cache_key_gen.generate_key("asdfghjklzxcvbnm", boo, *[1234, 12345134], **{})
        self.assertNotEqual(key1, None)
        self.assertEqual(len(key1), limit_key_length)

        cache_key_gen = CacheKeyGenerator(max_key_length=250)
        key2 = cache_key_gen.generate_key("xyz_{param_1}_{param_2}", boo, *[11, 22], **{})
        self.assertNotEqual(key2, None)
        self.assertEqual(key2, "xyz_11_22")

        key3 = cache_key_gen.generate_key("xyz_{param_1}_{param_2}", boo, *[11], **{})
        self.assertNotEqual(key3, None)
        self.assertEqual(key3, "xyz_11_param_2")

        key4 = cache_key_gen.generate_key("xyz_{param_1}_{param_2}", boo, *[], **{"param_2": "pp2"})
        self.assertNotEqual(key4, None)
        self.assertEqual(key4, "xyz_param_1_pp2")

    def test_cache_client_register(self):
        self.assertRaises(ValueError, self.not_exists_cache_client_name)

    def test_cash(self):
        TestCache.test_value = 100

        self.assertEqual(self.get_cache(), 100)
        TestCache.test_value = 200
        self.assertEqual(self.get_cache(), 100)
        sleep(2.3)
        self.assertEqual(self.get_cache(), 200)
        TestCache.test_value = 100
        self.assertEqual(self.get_cache(), 200)
        self.clear_cache()
        self.assertEqual(self.get_cache(), 100)

    def test_cash_with_param(self):
        TestCache.test_value = 100

        param = "some_val"
        self.assertEqual(self.get_cache_with_param(param), 100)
        TestCache.test_value = 200
        self.assertEqual(self.get_cache_with_param(param), 100)
        sleep(2.3)
        self.assertEqual(self.get_cache_with_param(param), 200)
        TestCache.test_value = 100
        self.assertEqual(self.get_cache_with_param("other_param"), 100)
        self.assertEqual(self.get_cache_with_param(param), 200)
        self.clear_cache_with_param(param)
        self.assertEqual(self.get_cache_with_param(param), 100)

    def test_cash_with_param_optional(self):
        TestCache.test_value = 100

        param = "some_val"
        self.assertEqual(self.get_cache_with_param_optional(param), 100)
        TestCache.test_value = 200
        self.assertEqual(self.get_cache_with_param_optional(param), 100)
        sleep(2.3)
        self.assertEqual(self.get_cache_with_param_optional(param), 200)
        TestCache.test_value = 100
        self.assertEqual(self.get_cache_with_param_optional("other_param"), 100)
        self.assertEqual(self.get_cache_with_param_optional(param), 200)
        self.clear_cache_with_param_optional(param)
        self.assertEqual(self.get_cache_with_param_optional(param), 100)

        self.assertEqual(self.get_cache_with_param_optional(param), 100)

        TestCache.test_value = 400
        self.assertEqual(self.get_cache_with_param_optional(param, 3, 4, "param_4_new"), 400)

        TestCache.test_value = 500
        self.assertEqual(self.get_cache_with_param_optional(param, 4), 500)

        TestCache.test_value = 600
        self.assertEqual(self.get_cache_with_param_optional(param, 4, 5), 600)

        TestCache.test_value = 700
        self.assertEqual(self.get_cache_with_param_optional(param, 4, 5, "__1"), 700)

        TestCache.test_value = 800
        self.assertEqual(self.get_cache_with_param_optional(param, 4, 5, "__2"), 800)

    def test_cash_only_param_optional(self):
        TestCache.test_value = 100
        self.assertEqual(self.get_cache_only_param_optional(), 100)
        TestCache.test_value = 200
        self.assertEqual(self.get_cache_only_param_optional(10, 20, 30, 40), 200)
        TestCache.test_value = 300
        self.assertEqual(self.get_cache_only_param_optional(param_4=40), 300)


    # Cache without params
    @Cache(key="test_cache_1", expire=timedelta(seconds=2))
    def get_cache(self):
        return TestCache.test_value

    @Cache(key="test_cache_1", invalidate=True)
    def clear_cache(self):
        pass

    # Cache with param
    @Cache(key="test_cache_param_{param_1}", expire=timedelta(seconds=2), cache_client_name=cache_client_name)
    def get_cache_with_param(self, param_1):
        return TestCache.test_value

    @Cache(key="test_cache_param_{param_1}", invalidate=True)
    def clear_cache_with_param(self, param_1):
        pass

    # Cache with optional
    @Cache(key="test_cache_param_{param_1}{param_2}{param_3}{param_4}", expire=timedelta(seconds=2))
    def get_cache_with_param_optional(self, param_1, param_2=2, param_3=None, param_4="param4"):
        return TestCache.test_value

    @Cache(key="test_cache_param_{param_1}{param_2}{param_3}{param_4}", invalidate=True, cache_client_name=cache_client_name)
    def clear_cache_with_param_optional(self, param_1, param_2=2, param_3=None, param_4="param4"):
        pass

    @Cache(key="test_cache_1", expire=timedelta(seconds=2), cache_client_name="sosososos")
    def not_exists_cache_client_name(self):
        return TestCache.test_value

    # Cache only with optional
    @Cache(key="test_cache_param_{param_1}{param_2}{param_3}{param_4}", expire=timedelta(seconds=2))
    def get_cache_only_param_optional(self, param_1=None, param_2=None, param_3=None, param_4=None):
        return TestCache.test_value

