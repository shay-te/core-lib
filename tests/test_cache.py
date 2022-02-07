import unittest
from datetime import timedelta, datetime
from time import sleep
from freezegun import freeze_time

from core_lib.cache.cache_decorator import Cache
from core_lib.cache.cache_handler_ram import CacheHandlerRam
from core_lib.core_lib import CoreLib

cache_client_name = "xyz"


class TestCache(unittest.TestCase):

    test_value = 100
    cache_duration = "2 seconds"

    @classmethod
    def setUpClass(cls):
        CoreLib.cache_registry.register(cache_client_name, CacheHandlerRam())

    @classmethod
    def tearDownClass(cls):
        CoreLib.cache_registry.unregister(cache_client_name)

    def test_cache_client_register(self):
        self.assertRaises(ValueError, self.not_exists_cache_client_name)

    def test_cash(self):
        self.clear_cache()
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
        sleep(2.3)
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
        sleep(2.3)
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

    def test_cache_is_expiring(self):
        self.clear_cache()
        TestCache.test_value = 100
        self.assertEqual(self.get_cache(), 100)
        TestCache.test_value = 200
        sleep(1)
        self.assertEqual(self.get_cache(), 100)
        sleep(1)
        self.assertEqual(self.get_cache(), 200)

    def test_cache_using_string(self):
        self.clear_cache()
        TestCache.cache_duration = "2 seconds"
        TestCache.test_value = 100
        self.assertEqual(self.get_cache_expire_string(), 100)
        TestCache.test_value = 200
        self.assertEqual(self.get_cache_expire_string(), 100)
        with freeze_time(datetime.today().replace(minute=datetime.now().minute + 1)):
            self.assertEqual(self.get_cache_expire_string(), 200)

        self.clear_cache()
        TestCache.cache_duration = "60 seconds"
        TestCache.test_value = 100
        self.assertEqual(self.get_cache_expire_string(), 100)
        TestCache.test_value = 200
        self.assertEqual(self.get_cache_expire_string(), 100)
        with freeze_time(datetime.today().replace(minute=datetime.now().minute + 1)):
            self.assertEqual(self.get_cache_expire_string(), 200)

        self.clear_cache()
        TestCache.cache_duration = "1 minute"
        TestCache.test_value = 100
        self.assertEqual(self.get_cache_expire_string(), 100)
        TestCache.test_value = 200
        self.assertEqual(self.get_cache_expire_string(), 100)
        with freeze_time(datetime.today().replace(minute=datetime.now().minute + 1)):
            self.assertEqual(self.get_cache_expire_string(), 200)

        self.clear_cache()
        TestCache.cache_duration = "1 day"
        TestCache.test_value = 100
        self.assertEqual(self.get_cache_expire_string(), 100)
        TestCache.test_value = 200
        self.assertEqual(self.get_cache_expire_string(), 100)
        with freeze_time(datetime.today() + timedelta(days=1)):
            self.assertEqual(self.get_cache_expire_string(), 200)

        self.clear_cache()
        TestCache.cache_duration = "1 week"
        TestCache.test_value = 100
        self.assertEqual(self.get_cache_expire_string(), 100)
        TestCache.test_value = 200
        self.assertEqual(self.get_cache_expire_string(), 100)
        with freeze_time(datetime.today() + timedelta(days=7)):
            self.assertEqual(self.get_cache_expire_string(), 200)

        self.clear_cache()
        TestCache.cache_duration = "1 month"
        TestCache.test_value = 100
        self.assertEqual(self.get_cache_expire_string(), 100)
        TestCache.test_value = 200
        self.assertEqual(self.get_cache_expire_string(), 100)
        with freeze_time(datetime.today().replace(month=datetime.now().month + 1)):
            self.assertEqual(self.get_cache_expire_string(), 200)

        self.clear_cache()
        TestCache.cache_duration = "1 year"
        TestCache.test_value = 100
        self.assertEqual(self.get_cache_expire_string(), 100)
        TestCache.test_value = 200
        self.assertEqual(self.get_cache_expire_string(), 100)
        with freeze_time(datetime.today().replace(year=datetime.now().year + 1)):
            self.assertEqual(self.get_cache_expire_string(), 200)

    @Cache(key="test_cache_1", expire=timedelta(seconds=2))
    def get_cache(self):
        return TestCache.test_value

    @Cache(key="test_cache_1", invalidate=True)
    def clear_cache(self):
        pass

    @Cache(key="test_cache_param_{param_1}", expire=timedelta(seconds=2), handler=cache_client_name)
    def get_cache_with_param(self, param_1):
        return TestCache.test_value

    @Cache(key="test_cache_param_{param_1}", invalidate=True)
    def clear_cache_with_param(self, param_1):
        pass

    @Cache(key="test_cache_param_{param_1}{param_2}{param_3}{param_4}", expire=timedelta(seconds=2))
    def get_cache_with_param_optional(self, param_1, param_2=2, param_3=None, param_4="param4"):
        return TestCache.test_value

    @Cache(key="test_cache_param_{param_1}{param_2}{param_3}{param_4}", invalidate=True, handler=cache_client_name)
    def clear_cache_with_param_optional(self, param_1, param_2=2, param_3=None, param_4="param4"):
        pass

    @Cache(key="test_cache_1", expire=timedelta(seconds=2), handler="sosososos")
    def not_exists_cache_client_name(self):
        return TestCache.test_value

    @Cache(key="test_cache_param_{param_1}{param_2}{param_3}{param_4}", expire=timedelta(seconds=2))
    def get_cache_only_param_optional(self, param_1=None, param_2=None, param_3=None, param_4=None):
        return TestCache.test_value

    @Cache(key="test_cache_1", expire=str(cache_duration))
    def get_cache_expire_string(self):
        return TestCache.test_value
