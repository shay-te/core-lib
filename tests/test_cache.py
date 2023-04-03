import unittest
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from time import sleep
from freezegun import freeze_time

from core_lib.cache.cache_decorator import Cache
from core_lib.cache.cache_handler_ram import CacheHandlerRam
from core_lib.core_lib import CoreLib

cache_client_name = "xyz"


class TestCache(unittest.TestCase):
    test_value = 100
    test_dict = {'value': '100'}
    test_tuple = ('value', '100')
    test_list = ['value', '100']
    test_string = "Hello World"
    test_set = {1.0, "Hello", (1, 2, 3)}

    @classmethod
    def setUpClass(cls):
        CoreLib.cache_registry.register(cache_client_name, CacheHandlerRam())

    @classmethod
    def tearDownClass(cls):
        CoreLib.cache_registry.unregister(cache_client_name)

    def test_cache_client_register(self):
        self.assertRaises(ValueError, self.not_exists_cache_client_name)

    def test_cache(self):
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

    def test_cache_with_param(self):
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

    def test_cache_with_param_optional(self):
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

    def test_cache_only_param_optional(self):
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
        # Seconds
        TestCache.test_value = 100
        self.assertEqual(self.get_cache_expire_string_seconds(), 100)
        TestCache.test_value = 200
        self.assertEqual(self.get_cache_expire_string_seconds(), 100)
        sleep(2.2)
        self.assertEqual(self.get_cache_expire_string_seconds(), 200)
        self.clear_cache_expire_string_seconds()
        TestCache.test_value = 100
        self.assertEqual(self.get_cache_expire_string_seconds(), 100)

        # Minute
        TestCache.test_value = 100
        self.assertEqual(self.get_cache_expire_string_minute(), 100)
        TestCache.test_value = 200
        self.assertEqual(self.get_cache_expire_string_minute(), 100)
        with freeze_time(datetime.utcnow() + timedelta(seconds=59)):
            self.assertEqual(self.get_cache_expire_string_minute(), 100)
        with freeze_time(datetime.utcnow() + timedelta(minutes=1)):
            self.assertEqual(self.get_cache_expire_string_minute(), 200)
        self.clear_cache_expire_string_minute()
        TestCache.test_value = 100
        self.assertEqual(self.get_cache_expire_string_minute(), 100)

        # Hour
        TestCache.test_value = 100
        self.assertEqual(self.get_cache_expire_string_hour(), 100)
        TestCache.test_value = 200
        self.assertEqual(self.get_cache_expire_string_hour(), 100)
        with freeze_time(datetime.utcnow() + timedelta(minutes=59)):
            self.assertEqual(self.get_cache_expire_string_hour(), 100)
        with freeze_time(datetime.utcnow() + timedelta(hours=1)):
            self.assertEqual(self.get_cache_expire_string_hour(), 200)
        self.clear_cache_expire_string_hour()
        TestCache.test_value = 100
        self.assertEqual(self.get_cache_expire_string_hour(), 100)

        # Day
        TestCache.test_value = 100
        self.assertEqual(self.get_cache_expire_string_day(), 100)
        TestCache.test_value = 200
        self.assertEqual(self.get_cache_expire_string_day(), 100)
        with freeze_time(datetime.utcnow() + timedelta(hours=23)):
            self.assertEqual(self.get_cache_expire_string_day(), 100)
        with freeze_time(datetime.utcnow() + timedelta(days=1)):
            self.assertEqual(self.get_cache_expire_string_day(), 200)
        self.clear_cache_expire_string_day()
        TestCache.test_value = 100
        self.assertEqual(self.get_cache_expire_string_day(), 100)

        # Week
        TestCache.test_value = 100
        self.assertEqual(self.get_cache_expire_string_week(), 100)
        TestCache.test_value = 200
        self.assertEqual(self.get_cache_expire_string_week(), 100)
        with freeze_time(datetime.today() + timedelta(days=6)):
            self.assertEqual(self.get_cache_expire_string_week(), 100)
        with freeze_time(datetime.today() + timedelta(days=7)):
            self.assertEqual(self.get_cache_expire_string_week(), 200)
        self.clear_cache_expire_string_week()
        TestCache.test_value = 100
        self.assertEqual(self.get_cache_expire_string_week(), 100)

        # Month
        TestCache.test_value = 100
        self.assertEqual(self.get_cache_expire_string_month(), 100)
        TestCache.test_value = 200
        self.assertEqual(self.get_cache_expire_string_month(), 100)
        with freeze_time(datetime.today() + timedelta(days=20)):
            self.assertEqual(self.get_cache_expire_string_month(), 100)
        with freeze_time(datetime.today() + relativedelta(months=1)):
            self.assertEqual(self.get_cache_expire_string_month(), 200)
        self.clear_cache_expire_string_month()
        TestCache.test_value = 100
        self.assertEqual(self.get_cache_expire_string_month(), 100)

        # Year
        TestCache.test_value = 100
        self.assertEqual(self.get_cache_expire_string_year(), 100)
        TestCache.test_value = 200
        self.assertEqual(self.get_cache_expire_string_year(), 100)
        with freeze_time(datetime.today() + relativedelta(months=11, days=20)):
            self.assertEqual(self.get_cache_expire_string_year(), 100)
        with freeze_time(datetime.today().replace(year=datetime.utcnow().year + 1)):
            self.assertEqual(self.get_cache_expire_string_year(), 200)
        self.clear_cache_expire_string_year()
        TestCache.test_value = 100
        self.assertEqual(self.get_cache_expire_string_year(), 100)

    def _test_empty_cache_helper(self, cache_data, empty_value, cache_empty_results):
        if cache_empty_results:
            self.clear_cache_empty()
            self.assertEqual(self.get_cache_empty_results(empty_value), empty_value)
            self.assertEqual(self.get_cache_empty_results(cache_data), empty_value)
            with freeze_time(datetime.utcnow() + timedelta(seconds=2)):
                self.assertEqual(self.get_cache_empty_results(cache_data), cache_data)
            self.assertEqual(self.get_cache_empty_results(empty_value), cache_data)
            with freeze_time(datetime.utcnow() + timedelta(seconds=4)):
                self.assertEqual(self.get_cache_empty_results(empty_value), empty_value)
        else:
            self.clear_cache_empty_false()
            self.assertEqual(self.get_dont_cache_empty_results(empty_value), empty_value)
            self.assertEqual(self.get_dont_cache_empty_results(cache_data), cache_data)
            self.assertEqual(self.get_dont_cache_empty_results(empty_value), cache_data)
            with freeze_time(datetime.utcnow() + timedelta(seconds=2)):
                self.assertEqual(self.get_dont_cache_empty_results(empty_value), empty_value)
            self.assertEqual(self.get_dont_cache_empty_results(cache_data), cache_data)

    def test_cache_empty(self):
        self._test_empty_cache_helper(TestCache.test_dict, {}, True)
        self._test_empty_cache_helper(TestCache.test_tuple, (), True)
        self._test_empty_cache_helper(TestCache.test_list, [], True)
        self._test_empty_cache_helper(TestCache.test_string, "", True)
        self._test_empty_cache_helper(TestCache.test_set, set(), True)

    def test_cache_empty_false(self):
        self._test_empty_cache_helper(TestCache.test_dict, {}, False)
        self._test_empty_cache_helper(TestCache.test_tuple, (), False)
        self._test_empty_cache_helper(TestCache.test_list, [], False)
        self._test_empty_cache_helper(TestCache.test_string, "", False)
        self._test_empty_cache_helper(TestCache.test_set, set(), False)

    CACHE_TEST = 'test_cache_1'

    @Cache(key=CACHE_TEST, expire=timedelta(seconds=2))
    def get_cache(self):
        return TestCache.test_value

    @Cache(key=CACHE_TEST, invalidate=True)
    def clear_cache(self):
        pass

    CACHE_WITH_PARAMS = 'test_cache_param_{param_1}'

    @Cache(key=CACHE_WITH_PARAMS, expire=timedelta(seconds=2), handler_name=cache_client_name)
    def get_cache_with_param(self, param_1):
        return TestCache.test_value

    @Cache(key=CACHE_WITH_PARAMS, invalidate=True)
    def clear_cache_with_param(self, param_1):
        pass

    CACHE_WITH_PARAMS_OPTIONAL = 'test_cache_param_{param_1}{param_2}{param_3}{param_4}'

    @Cache(key=CACHE_WITH_PARAMS_OPTIONAL, expire=timedelta(seconds=2))
    def get_cache_with_param_optional(self, param_1, param_2=2, param_3=None, param_4="param4"):
        return TestCache.test_value

    @Cache(key=CACHE_WITH_PARAMS_OPTIONAL, invalidate=True, handler_name=cache_client_name)
    def clear_cache_with_param_optional(self, param_1, param_2=2, param_3=None, param_4="param4"):
        pass

    @Cache(key=CACHE_TEST, expire=timedelta(seconds=2), handler_name="sosososos")
    def not_exists_cache_client_name(self):
        return TestCache.test_value

    @Cache(key=CACHE_WITH_PARAMS_OPTIONAL, expire=timedelta(seconds=2))
    def get_cache_only_param_optional(self, param_1=None, param_2=None, param_3=None, param_4=None):
        return TestCache.test_value

    CACHE_EXP_STR_SECONDS = 'test_cache_expire_string_seconds'

    @Cache(key=CACHE_EXP_STR_SECONDS, expire="2 second")
    def get_cache_expire_string_seconds(self):
        return TestCache.test_value

    @Cache(key=CACHE_EXP_STR_SECONDS, invalidate=True)
    def clear_cache_expire_string_seconds(self):
        pass

    CACHE_EXP_STR_MINUTES = 'test_cache_expire_string_minute'

    @Cache(key=CACHE_EXP_STR_MINUTES, expire="1 minute")
    def get_cache_expire_string_minute(self):
        return TestCache.test_value

    @Cache(key=CACHE_EXP_STR_MINUTES, invalidate=True)
    def clear_cache_expire_string_minute(self):
        pass

    CACHE_EXP_STR_HOUR = 'test_cache_expire_string_hour'

    @Cache(key=CACHE_EXP_STR_HOUR, expire="1 hour")
    def get_cache_expire_string_hour(self):
        return TestCache.test_value

    @Cache(key=CACHE_EXP_STR_HOUR, invalidate=True)
    def clear_cache_expire_string_hour(self):
        pass

    CACHE_EXP_STR_DAY = 'test_cache_expire_string_day'

    @Cache(key=CACHE_EXP_STR_DAY, expire="1 day")
    def get_cache_expire_string_day(self):
        return TestCache.test_value

    @Cache(key=CACHE_EXP_STR_DAY, invalidate=True)
    def clear_cache_expire_string_day(self):
        pass

    CACHE_EXP_STR_WEEK = 'test_cache_expire_string_week'

    @Cache(key=CACHE_EXP_STR_WEEK, expire="1 week")
    def get_cache_expire_string_week(self):
        return TestCache.test_value

    @Cache(key=CACHE_EXP_STR_WEEK, invalidate=True)
    def clear_cache_expire_string_week(self):
        pass

    CACHE_EXP_STR_MONTH = 'test_cache_expire_string_month'

    @Cache(key=CACHE_EXP_STR_MONTH, expire="1 month")
    def get_cache_expire_string_month(self):
        return TestCache.test_value

    @Cache(key=CACHE_EXP_STR_MONTH, invalidate=True)
    def clear_cache_expire_string_month(self):
        pass

    CACHE_EXP_STR_YEAR = 'test_cache_expire_string_year'

    @Cache(key=CACHE_EXP_STR_YEAR, expire="1 year")
    def get_cache_expire_string_year(self):
        return TestCache.test_value

    @Cache(key=CACHE_EXP_STR_YEAR, invalidate=True)
    def clear_cache_expire_string_year(self):
        pass

    CACHE_EMPTY_RESULTS = 'test_cache_empty_results'

    @Cache(key=CACHE_EMPTY_RESULTS, expire=timedelta(seconds=2))
    def get_cache_empty_results(self, param):
        return param

    @Cache(key=CACHE_EMPTY_RESULTS, invalidate=True)
    def clear_cache_empty(self):
        pass

    CACHE_EMPTY_RESULTS_FALSE = 'test_cache_empty_results_false'

    @Cache(key=CACHE_EMPTY_RESULTS_FALSE, cache_empty_result=False, expire=timedelta(seconds=2))
    def get_dont_cache_empty_results(self, param):
        return param

    @Cache(key=CACHE_EMPTY_RESULTS_FALSE, invalidate=True)
    def clear_cache_empty_false(self):
        pass
