"""`@Cache` on a `CacheHandlerRedis`: a miss stores the result in Redis, a hit answers from Redis without calling the
function, and an invalidation clears exactly its key, also around `@Transaction()`.

Runs only when `CORE_LIB_TEST_REDIS_URL` names a THROWAWAY Redis (`redis://127.0.0.1:56379/0`); skipped
otherwise. Every test empties that server, so never point it at one holding data.
"""
import json
import os
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from time import sleep

import redis

from core_lib.cache.cache_decorator import Cache
from core_lib.cache.cache_handler_redis import CacheHandlerRedis
from core_lib.connection.transaction_decorator import Transaction
from core_lib.core_lib import CoreLib

REDIS_URL = os.environ.get('CORE_LIB_TEST_REDIS_URL')
CACHE_HANDLER_NAME = 'test_cache_decorator_redis'
CACHE_KEY_WIDGET = 'redis_widget_{widget_id}'
CACHE_KEY_WIDGET_FRESH = 'redis_widget_fresh_{widget_id}'
CACHE_KEY_WIDGET_SHORT = 'redis_widget_short_{widget_id}'
CACHE_KEY_WIDGET_BLINK = 'redis_widget_blink_{widget_id}'
CACHE_KEY_WIDGET_HOURLY = 'redis_widget_hourly_{widget_id}'
CACHE_KEY_WIDGET_NON_EMPTY = 'redis_widget_non_empty_{widget_id}'
CACHE_KEY_WIDGET_BY_NAME = 'redis_widget_name_{name}'
CACHE_KEY_WIDGET_BY_LABEL = 'redis_widget_label_{label}'
LABEL_KEY_LENGTH = 30
FRESH_EXPIRE = timedelta(minutes=5)
SHORT_EXPIRE = timedelta(seconds=1)
BLINK_EXPIRE = timedelta(milliseconds=500)
NO_EXPIRY_TTL = -1  # the TTL Redis reports for a key stored with no expiry
CACHEABLE_RESULTS = {
    'dict': {'name': 'acme', 'tags': ['widget']},
    'list': ['acme', 1, None],
    'int': 42,
    'str': 'acme widget',
    'true': True,
    'zero': 0,
    'false': False,
    'empty_str': '',
    'empty_list': [],
    'empty_dict': {},
}
EMPTY_RESULTS = {'zero': 0, 'false': False, 'empty_str': '', 'empty_list': [], 'empty_dict': {}}
THREAD_COUNT = 16


class WidgetCatalogue(object):
    """The decorated reads count their calls, so a test can tell a hit (no call) from a miss."""

    def __init__(self):
        self.names = {}
        self.calls = 0

    def _read(self, widget_id):
        self.calls += 1
        return self.names[widget_id]

    @Cache(CACHE_KEY_WIDGET, handler_name=CACHE_HANDLER_NAME)
    def get(self, widget_id: int):
        return self._read(widget_id)

    @Cache(CACHE_KEY_WIDGET_FRESH, handler_name=CACHE_HANDLER_NAME, expire=FRESH_EXPIRE)
    def get_fresh(self, widget_id: int):
        return self._read(widget_id)

    @Cache(CACHE_KEY_WIDGET_SHORT, handler_name=CACHE_HANDLER_NAME, expire=SHORT_EXPIRE)
    def get_short(self, widget_id: int):
        return self._read(widget_id)

    @Cache(CACHE_KEY_WIDGET_BLINK, handler_name=CACHE_HANDLER_NAME, expire=BLINK_EXPIRE)
    def get_blink(self, widget_id: int):
        return self._read(widget_id)

    @Cache(CACHE_KEY_WIDGET_HOURLY, handler_name=CACHE_HANDLER_NAME, expire='1 hour')
    def get_hourly(self, widget_id: int):
        return self._read(widget_id)

    @Cache(CACHE_KEY_WIDGET_NON_EMPTY, handler_name=CACHE_HANDLER_NAME, cache_empty_result=False)
    def get_non_empty(self, widget_id: int):
        return self._read(widget_id)

    @Cache(CACHE_KEY_WIDGET_BY_NAME, handler_name=CACHE_HANDLER_NAME)
    def get_by_name(self, name: str):
        return self._read(name)

    @Cache(CACHE_KEY_WIDGET_BY_LABEL, handler_name=CACHE_HANDLER_NAME, max_key_length=LABEL_KEY_LENGTH)
    def get_by_label(self, label: str):
        return self._read(label)

    @Cache(CACHE_KEY_WIDGET, handler_name=CACHE_HANDLER_NAME, invalidate=True)
    def rename(self, widget_id: int, name: str):
        self.names[widget_id] = name

    @Cache(CACHE_KEY_WIDGET, handler_name=CACHE_HANDLER_NAME, invalidate=True)
    def fail_to_rename(self, widget_id: int, name: str):
        raise RuntimeError('the rename failed')

    @Transaction()
    def get_in_transaction(self, widget_id: int):
        return self.get(widget_id)

    @Transaction()
    def rename_in_transaction(self, widget_id: int, name: str, redis_client: redis.Redis) -> int:
        self.rename(widget_id, name)
        return redis_client.exists(CACHE_KEY_WIDGET.format(widget_id=widget_id))  # still there before the commit

    @Transaction()
    def rename_then_roll_back(self, widget_id: int, name: str):
        self.rename(widget_id, name)
        raise RuntimeError('the transaction failed')


@unittest.skipUnless(REDIS_URL, 'needs a throwaway Redis server: set CORE_LIB_TEST_REDIS_URL')
class TestCacheDecoratorRedis(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.redis_client = redis.from_url(REDIS_URL)  # the test's own view of what the server holds
        CoreLib.cache_registry.register(CACHE_HANDLER_NAME, CacheHandlerRedis(REDIS_URL))

    @classmethod
    def tearDownClass(cls):
        CoreLib.cache_registry.unregister(CACHE_HANDLER_NAME)
        cls.redis_client.flushall()
        cls.redis_client.close()

    def setUp(self):
        self.redis_client.flushall()
        self.widget_catalogue = WidgetCatalogue()

    def _stored(self, key: str):
        return json.loads(self.redis_client.get(key))

    def _use_a_second_handler(self):
        # the same Redis reached through a new handler and connection, as a second process would
        first_handler = CoreLib.cache_registry.get(CACHE_HANDLER_NAME)
        CoreLib.cache_registry.unregister(CACHE_HANDLER_NAME)
        CoreLib.cache_registry.register(CACHE_HANDLER_NAME, CacheHandlerRedis(REDIS_URL))
        self.addCleanup(CoreLib.cache_registry.register, CACHE_HANDLER_NAME, first_handler)
        self.addCleanup(CoreLib.cache_registry.unregister, CACHE_HANDLER_NAME)

    def test_a_miss_stores_the_result_with_no_expiry(self):
        self.widget_catalogue.names[7] = 'acme'
        self.assertEqual('acme', self.widget_catalogue.get(7))
        self.assertEqual('acme', self._stored('redis_widget_7'))
        self.assertEqual(NO_EXPIRY_TTL, self.redis_client.ttl('redis_widget_7'))
        self.assertEqual(1, self.widget_catalogue.calls)

    def test_every_cacheable_result_is_stored_and_the_next_call_is_a_hit(self):
        for widget_id, (label, result) in enumerate(CACHEABLE_RESULTS.items(), start=100):
            with self.subTest(label):
                self.widget_catalogue.names[widget_id] = result
                calls_before = self.widget_catalogue.calls
                first_read = self.widget_catalogue.get(widget_id)
                second_read = self.widget_catalogue.get(widget_id)
                self.assertEqual(json.dumps(result), json.dumps(first_read))
                self.assertEqual(json.dumps(result), json.dumps(second_read))
                self.assertEqual((type(result), type(result)), (type(first_read), type(second_read)))
                self.assertEqual(calls_before + 1, self.widget_catalogue.calls)
                self.assertEqual(result, self._stored('redis_widget_{}'.format(widget_id)))

    def test_a_hit_answers_from_redis_not_from_the_function(self):
        self.widget_catalogue.names[8] = 'acme'
        first_read = self.widget_catalogue.get(8)
        self.widget_catalogue.names[8] = 'widget'  # changed behind the cache, so only a hit can still answer 'acme'
        second_read = self.widget_catalogue.get(8)
        self.assertEqual('acme', first_read)
        self.assertEqual('acme', second_read)
        self.assertEqual(1, self.widget_catalogue.calls)

    def test_a_hit_is_served_to_a_second_handler_on_the_same_redis(self):
        self.widget_catalogue.names[8] = 'acme'
        self.widget_catalogue.get(8)
        self._use_a_second_handler()
        self.widget_catalogue.names[8] = 'widget'
        self.assertEqual('acme', self.widget_catalogue.get(8))
        self.assertEqual(1, self.widget_catalogue.calls)

    def test_keys_of_two_methods_never_share_an_entry(self):
        self.widget_catalogue.names[9] = 'acme'
        self.widget_catalogue.get(9)
        self.widget_catalogue.names[9] = 'widget'
        self.assertEqual('widget', self.widget_catalogue.get_fresh(9))
        self.assertEqual('acme', self._stored('redis_widget_9'))
        self.assertEqual('widget', self._stored('redis_widget_fresh_9'))
        self.assertEqual(2, self.widget_catalogue.calls)

    def test_a_hit_returns_a_dict_with_its_int_keys_turned_to_strings(self):
        self.widget_catalogue.names[10] = {1: 'acme', 2: 'widget'}
        cold_read = self.widget_catalogue.get(10)
        hot_read = self.widget_catalogue.get(10)
        self.assertEqual({1: 'acme', 2: 'widget'}, cold_read)
        self.assertEqual({'1': 'acme', '2': 'widget'}, hot_read)

    def test_the_decorator_expire_reaches_redis(self):
        self.widget_catalogue.names[11] = 'acme'
        self.assertEqual('acme', self.widget_catalogue.get_fresh(11))
        self.assertEqual('acme', self._stored('redis_widget_fresh_11'))
        self.assertIn(self.redis_client.ttl('redis_widget_fresh_11'), (299, 300))

    def test_a_string_expire_reaches_redis(self):
        self.widget_catalogue.names[12] = 'acme'
        self.widget_catalogue.get_hourly(12)
        self.assertEqual(3600, self.redis_client.ttl('redis_widget_hourly_12'))  # '1 hour' is kept exactly

    def test_an_expire_under_one_second_is_cached_for_exactly_that_time(self):
        self.widget_catalogue.names[14] = 'acme'
        self.assertEqual('acme', self.widget_catalogue.get_blink(14))
        remaining_ms = self.redis_client.pttl('redis_widget_blink_14')
        self.assertGreater(remaining_ms, 400)
        self.assertLessEqual(remaining_ms, 500)
        self.widget_catalogue.names[14] = 'widget'
        sleep(0.2)
        self.assertEqual('acme', self.widget_catalogue.get_blink(14))
        sleep(0.4)
        self.assertEqual('widget', self.widget_catalogue.get_blink(14))
        self.assertEqual(2, self.widget_catalogue.calls)

    def test_an_expired_entry_is_recomputed_and_stored_again(self):
        self.widget_catalogue.names[13] = 'acme'
        self.assertEqual('acme', self.widget_catalogue.get_short(13))
        self.widget_catalogue.names[13] = 'widget'
        sleep(0.5)
        self.assertEqual('acme', self.widget_catalogue.get_short(13))
        sleep(0.7)
        self.assertEqual('widget', self.widget_catalogue.get_short(13))
        self.assertEqual('widget', self._stored('redis_widget_short_13'))
        self.assertEqual(2, self.widget_catalogue.calls)

    def test_a_none_result_is_never_stored(self):
        self.widget_catalogue.names[14] = None
        self.assertIsNone(self.widget_catalogue.get(14))
        self.assertIsNone(self.widget_catalogue.get(14))
        self.assertEqual(0, self.redis_client.exists('redis_widget_14'))
        self.assertEqual(2, self.widget_catalogue.calls)

    def test_cache_empty_result_false_stores_no_empty_result(self):
        for widget_id, (label, result) in enumerate(EMPTY_RESULTS.items(), start=200):
            with self.subTest(label):
                self.widget_catalogue.names[widget_id] = result
                calls_before = self.widget_catalogue.calls
                self.assertEqual(result, self.widget_catalogue.get_non_empty(widget_id))
                self.assertEqual(result, self.widget_catalogue.get_non_empty(widget_id))
                self.assertEqual(0, self.redis_client.exists('redis_widget_non_empty_{}'.format(widget_id)))
                self.assertEqual(calls_before + 2, self.widget_catalogue.calls)

    def test_cache_empty_result_false_still_stores_a_non_empty_result(self):
        self.widget_catalogue.names[15] = 'acme'
        self.widget_catalogue.get_non_empty(15)
        self.widget_catalogue.get_non_empty(15)
        self.assertEqual('acme', self._stored('redis_widget_non_empty_15'))
        self.assertEqual(1, self.widget_catalogue.calls)

    def test_a_result_redis_cannot_hold_fails_the_call_and_stores_nothing(self):
        for widget_id, result in ((16, {'acme', 'widget'}), (17, 1.5), (18, ('acme', 1))):
            with self.subTest(type(result).__name__):
                self.widget_catalogue.names[widget_id] = result
                with self.assertRaises(ValueError):
                    self.widget_catalogue.get(widget_id)
                self.assertEqual(0, self.redis_client.exists('redis_widget_{}'.format(widget_id)))

    def test_an_exception_in_the_function_stores_nothing(self):
        with self.assertRaises(KeyError):
            self.widget_catalogue.get(19)  # no name for 19
        self.assertEqual(0, self.redis_client.exists('redis_widget_19'))
        self.widget_catalogue.names[19] = 'acme'
        self.assertEqual('acme', self.widget_catalogue.get(19))
        self.assertEqual('acme', self._stored('redis_widget_19'))

    def test_invalidate_clears_the_key_and_the_next_read_recomputes(self):
        self.widget_catalogue.names[20] = 'acme'
        self.assertEqual('acme', self.widget_catalogue.get(20))
        self.widget_catalogue.rename(20, 'widget')
        self.assertEqual(0, self.redis_client.exists('redis_widget_20'))
        self.assertEqual('widget', self.widget_catalogue.get(20))
        self.assertEqual('widget', self._stored('redis_widget_20'))
        self.assertEqual(2, self.widget_catalogue.calls)

    def test_invalidate_clears_only_its_own_key(self):
        self.widget_catalogue.names[21] = 'acme'
        self.widget_catalogue.names[22] = 'widget'
        self.widget_catalogue.get(21)
        self.widget_catalogue.get(22)
        self.widget_catalogue.get_fresh(21)
        self.widget_catalogue.rename(21, 'reviewer')
        self.assertEqual(0, self.redis_client.exists('redis_widget_21'))
        self.assertEqual('widget', self._stored('redis_widget_22'))
        self.assertEqual('acme', self._stored('redis_widget_fresh_21'))

    def test_invalidate_of_a_key_never_cached_does_nothing(self):
        self.widget_catalogue.names[23] = 'acme'
        self.widget_catalogue.get(23)
        self.widget_catalogue.rename(24, 'widget')
        self.assertEqual('acme', self._stored('redis_widget_23'))
        self.assertEqual(1, self.redis_client.dbsize())

    def test_an_invalidation_that_raises_keeps_the_cached_value(self):
        self.widget_catalogue.names[25] = 'acme'
        self.widget_catalogue.get(25)
        with self.assertRaises(RuntimeError):
            self.widget_catalogue.fail_to_rename(25, 'widget')
        self.assertEqual('acme', self._stored('redis_widget_25'))
        self.assertEqual('acme', self.widget_catalogue.get(25))
        self.assertEqual(1, self.widget_catalogue.calls)

    def test_spaces_in_a_key_become_underscores_so_both_spellings_share_one_entry(self):
        self.widget_catalogue.names['acme widget'] = 'first'
        self.widget_catalogue.names['acme_widget'] = 'second'
        self.assertEqual('first', self.widget_catalogue.get_by_name('acme widget'))
        self.assertEqual('first', self._stored('redis_widget_name_acme_widget'))
        self.assertEqual('first', self.widget_catalogue.get_by_name('acme_widget'))
        self.assertEqual(1, self.redis_client.dbsize())

    def test_a_key_is_cut_to_max_key_length_so_labels_alike_up_to_it_share_one_entry(self):
        long_label = 'acme-widget-reviewer-one'
        other_long_label = 'acme-widget-reviewer-two'
        self.widget_catalogue.names[long_label] = 'first'
        self.widget_catalogue.names[other_long_label] = 'second'
        self.assertEqual('first', self.widget_catalogue.get_by_label(long_label))
        self.assertEqual('first', self._stored('redis_widget_label_acme-widget'))
        self.assertEqual('first', self.widget_catalogue.get_by_label(other_long_label))
        self.assertEqual([b'redis_widget_label_acme-widget'], self.redis_client.keys('*'))
        self.assertEqual(LABEL_KEY_LENGTH, len('redis_widget_label_acme-widget'))

    def test_a_read_inside_a_transaction_neither_reads_nor_fills_redis(self):
        self.widget_catalogue.names[26] = 'acme'
        self.widget_catalogue.get(26)
        self.widget_catalogue.names[26] = 'widget'
        self.widget_catalogue.names[27] = 'reviewer'
        self.assertEqual('widget', self.widget_catalogue.get_in_transaction(26))
        self.assertEqual('reviewer', self.widget_catalogue.get_in_transaction(27))
        self.assertEqual('acme', self._stored('redis_widget_26'))
        self.assertEqual(0, self.redis_client.exists('redis_widget_27'))

    def test_an_invalidation_inside_a_transaction_clears_redis_only_after_the_commit(self):
        self.widget_catalogue.names[28] = 'acme'
        self.widget_catalogue.get(28)
        existed_before_the_commit = self.widget_catalogue.rename_in_transaction(28, 'widget', self.redis_client)
        self.assertEqual(1, existed_before_the_commit)
        self.assertEqual(0, self.redis_client.exists('redis_widget_28'))
        self.assertEqual('widget', self.widget_catalogue.get(28))

    def test_an_invalidation_inside_a_rolled_back_transaction_keeps_the_cached_value(self):
        self.widget_catalogue.names[29] = 'acme'
        self.widget_catalogue.get(29)
        with self.assertRaises(RuntimeError):
            self.widget_catalogue.rename_then_roll_back(29, 'widget')
        self.assertEqual('acme', self._stored('redis_widget_29'))
        self.assertEqual(NO_EXPIRY_TTL, self.redis_client.ttl('redis_widget_29'))

    def test_concurrent_reads_of_different_keys_never_get_each_others_results(self):
        for widget_id in range(THREAD_COUNT):
            self.widget_catalogue.names[widget_id + 300] = {'widget': widget_id + 300}

        def read_twice(widget_id: int) -> list:
            return [self.widget_catalogue.get(widget_id), self.widget_catalogue.get(widget_id)]

        widget_ids = [widget_id + 300 for widget_id in range(THREAD_COUNT)]
        with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
            reads = list(executor.map(read_twice, widget_ids))
        self.assertEqual([[{'widget': widget_id}] * 2 for widget_id in widget_ids], reads)
        self.assertEqual(THREAD_COUNT, self.redis_client.dbsize())
