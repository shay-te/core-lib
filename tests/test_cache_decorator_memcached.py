"""`@Cache` on a `CacheHandlerMemcached`: a miss stores the result in memcached, a hit answers from memcached without
calling the function, an invalidation clears exactly its key, also around `@Transaction()`, and a result memcached
cannot keep still reaches the caller.

Runs only when `CORE_LIB_TEST_MEMCACHED_URL` names a THROWAWAY memcached (`127.0.0.1:51211`); skipped otherwise.
Every test empties that server, so never point it at one holding data. memcached's clock ticks once a second.
"""
import json
import os
import socket
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from time import sleep

from memcache import Client

from core_lib.cache.cache_decorator import Cache
from core_lib.cache.cache_handler_memcached import CacheHandlerMemcached
from core_lib.connection.transaction_decorator import Transaction
from core_lib.core_lib import CoreLib

MEMCACHED_URL = os.environ.get('CORE_LIB_TEST_MEMCACHED_URL')
CACHE_HANDLER_NAME = 'test_cache_decorator_memcached'
CACHE_KEY_WIDGET = 'memcached_widget_{widget_id}'
CACHE_KEY_WIDGET_FRESH = 'memcached_widget_fresh_{widget_id}'
CACHE_KEY_WIDGET_SHORT = 'memcached_widget_short_{widget_id}'
CACHE_KEY_WIDGET_BLINK = 'memcached_widget_blink_{widget_id}'
CACHE_KEY_WIDGET_HOURLY = 'memcached_widget_hourly_{widget_id}'
CACHE_KEY_WIDGET_MONTHLY = 'memcached_widget_monthly_{widget_id}'
CACHE_KEY_WIDGET_NON_EMPTY = 'memcached_widget_non_empty_{widget_id}'
CACHE_KEY_WIDGET_BY_NAME = 'memcached_widget_name_{name}'
CACHE_KEY_WIDGET_BY_LABEL = 'memcached_widget_label_{label}'
LABEL_KEY_LENGTH = 34
FRESH_EXPIRE = timedelta(minutes=5)
SHORT_EXPIRE = timedelta(seconds=2)
BLINK_EXPIRE = timedelta(milliseconds=500)
MONTHLY_EXPIRE = timedelta(days=31)
NO_EXPIRY_TTL = -1  # the TTL memcached reports for an item stored with no expiry
ITEM_LIMIT_BYTES = 1024 * 1024
TTL_READ_ATTEMPTS = 3
# over 30 days memcached takes a Unix time and reads it against its OWN clock, which can lag the client's (a
# Docker VM that slept lags by minutes): such a TTL reads longer by that lag, measured from `stats time`
ABSOLUTE_EXPIRE_CLOCK_SLACK_SECONDS = 2  # the once-a-second tick of both clocks
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
NAMES_MAKING_A_REFUSED_KEY = {  # @Cache itself turns a space into `_` and removes \n and \r
    'tab': 'acme\twidget',
    'null_character': 'acme\x00widget',
    'delete_character': 'acme\x7fwidget',
    'long_non_ascii': '\u05e9' * 200,  # a 222-character key of 422 bytes: memcached allows 250 bytes
}
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

    @Cache(CACHE_KEY_WIDGET_MONTHLY, handler_name=CACHE_HANDLER_NAME, expire=MONTHLY_EXPIRE)
    def get_monthly(self, widget_id: int):
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
    def rename_in_transaction(self, widget_id: int, name: str, memcached_client: Client) -> bool:
        self.rename(widget_id, name)
        # still there before the commit
        return memcached_client.get(CACHE_KEY_WIDGET.format(widget_id=widget_id)) is not None

    @Transaction()
    def rename_then_roll_back(self, widget_id: int, name: str):
        self.rename(widget_id, name)
        raise RuntimeError('the transaction failed')


@unittest.skipUnless(MEMCACHED_URL, 'needs a throwaway memcached server: set CORE_LIB_TEST_MEMCACHED_URL')
class TestCacheDecoratorMemcached(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.memcached_client = Client([MEMCACHED_URL])  # the test's own view of what the server holds
        CoreLib.cache_registry.register(CACHE_HANDLER_NAME, CacheHandlerMemcached(MEMCACHED_URL))

    @classmethod
    def tearDownClass(cls):
        CoreLib.cache_registry.get(CACHE_HANDLER_NAME).memcached_client.disconnect_all()
        CoreLib.cache_registry.unregister(CACHE_HANDLER_NAME)
        cls.memcached_client.flush_all()
        cls.memcached_client.disconnect_all()

    def setUp(self):
        self.memcached_client.flush_all()
        self.widget_catalogue = WidgetCatalogue()

    def _stored(self, key: str):
        return json.loads(self.memcached_client.get(key))

    def _is_stored(self, key: str) -> bool:
        return self.memcached_client.get(key) is not None

    def _server_clock_lag(self) -> float:
        """How far memcached's own clock is behind this machine's, read from `stats time`."""
        host, port = MEMCACHED_URL.rsplit(':', 1)
        with socket.create_connection((host, int(port))) as connection:
            connection.sendall(b'stats\r\n')
            reply = b''
            while not reply.endswith(b'END\r\n'):
                reply += connection.recv(4096)
        server_time = [line for line in reply.decode().split('\r\n') if line.startswith('STAT time ')][0].split()[2]
        return time.time() - int(server_time)

    def _server_ttl(self, key: str):
        """The TTL memcached itself holds for `key` (-1 = no expiry), or None when it holds no such item."""
        host, port = MEMCACHED_URL.rsplit(':', 1)
        with socket.create_connection((host, int(port))) as connection:
            connection.sendall(b'mg ' + key.encode() + b' t\r\n')
            reply = connection.recv(1024).decode()
        if reply.startswith('EN'):
            return None
        return int(reply.split(' t')[1].split()[0])

    def _use_handler(self, cache_handler: CacheHandlerMemcached):
        first_handler = CoreLib.cache_registry.get(CACHE_HANDLER_NAME)
        CoreLib.cache_registry.unregister(CACHE_HANDLER_NAME)
        CoreLib.cache_registry.register(CACHE_HANDLER_NAME, cache_handler)
        self.addCleanup(cache_handler.memcached_client.disconnect_all)
        self.addCleanup(CoreLib.cache_registry.register, CACHE_HANDLER_NAME, first_handler)
        self.addCleanup(CoreLib.cache_registry.unregister, CACHE_HANDLER_NAME)

    def _unreachable_cache_handler(self) -> CacheHandlerMemcached:
        with socket.socket() as unused_port_socket:
            unused_port_socket.bind(('127.0.0.1', 0))
            unused_port = unused_port_socket.getsockname()[1]
        return CacheHandlerMemcached('127.0.0.1:{}'.format(unused_port))

    def test_a_miss_stores_the_result_with_no_expiry(self):
        self.widget_catalogue.names[7] = 'acme'
        self.assertEqual('acme', self.widget_catalogue.get(7))
        self.assertEqual('acme', self._stored('memcached_widget_7'))
        self.assertEqual(NO_EXPIRY_TTL, self._server_ttl('memcached_widget_7'))
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
                self.assertEqual(result, self._stored('memcached_widget_{}'.format(widget_id)))

    def test_a_hit_answers_from_memcached_not_from_the_function(self):
        self.widget_catalogue.names[8] = 'acme'
        first_read = self.widget_catalogue.get(8)
        self.widget_catalogue.names[8] = 'widget'  # changed behind the cache, so only a hit can still answer 'acme'
        second_read = self.widget_catalogue.get(8)
        self.assertEqual('acme', first_read)
        self.assertEqual('acme', second_read)
        self.assertEqual(1, self.widget_catalogue.calls)

    def test_a_hit_is_served_to_a_second_handler_on_the_same_memcached(self):
        self.widget_catalogue.names[8] = 'acme'
        self.widget_catalogue.get(8)
        self._use_handler(CacheHandlerMemcached(MEMCACHED_URL))  # as a second process would reach it
        self.widget_catalogue.names[8] = 'widget'
        self.assertEqual('acme', self.widget_catalogue.get(8))
        self.assertEqual(1, self.widget_catalogue.calls)

    def test_keys_of_two_methods_never_share_an_entry(self):
        self.widget_catalogue.names[9] = 'acme'
        self.widget_catalogue.get(9)
        self.widget_catalogue.names[9] = 'widget'
        self.assertEqual('widget', self.widget_catalogue.get_fresh(9))
        self.assertEqual('acme', self._stored('memcached_widget_9'))
        self.assertEqual('widget', self._stored('memcached_widget_fresh_9'))
        self.assertEqual(2, self.widget_catalogue.calls)

    def test_a_hit_returns_a_dict_with_its_int_keys_turned_to_strings(self):
        self.widget_catalogue.names[10] = {1: 'acme', 2: 'widget'}
        cold_read = self.widget_catalogue.get(10)
        hot_read = self.widget_catalogue.get(10)
        self.assertEqual({1: 'acme', 2: 'widget'}, cold_read)
        self.assertEqual({'1': 'acme', '2': 'widget'}, hot_read)

    def test_the_decorator_expire_reaches_memcached(self):
        self.widget_catalogue.names[11] = 'acme'
        self.assertEqual('acme', self.widget_catalogue.get_fresh(11))
        self.assertEqual('acme', self._stored('memcached_widget_fresh_11'))
        self.assertIn(self._server_ttl('memcached_widget_fresh_11'), (299, 300))

    def test_a_string_expire_reaches_memcached_as_exactly_the_time_written(self):
        self.widget_catalogue.names[12] = 'acme'
        ttls = []
        for _ in range(TTL_READ_ATTEMPTS):  # the clock ticks once a second: the best of three reads is exact
            self.memcached_client.delete('memcached_widget_hourly_12')
            self.widget_catalogue.get_hourly(12)
            ttls.append(self._server_ttl('memcached_widget_hourly_12'))
        self.assertEqual(3600, max(ttls))  # '1 hour' is kept exactly; the parser used to fall short to 3599.98

    def test_an_expire_over_thirty_days_is_cached_and_hit(self):
        self.widget_catalogue.names[13] = 'acme'
        self.assertEqual('acme', self.widget_catalogue.get_monthly(13))
        self.widget_catalogue.names[13] = 'widget'
        self.assertEqual('acme', self.widget_catalogue.get_monthly(13))
        self.assertEqual(1, self.widget_catalogue.calls)
        expected = int(MONTHLY_EXPIRE.total_seconds()) + self._server_clock_lag()
        ttl = self._server_ttl('memcached_widget_monthly_13')
        self.assertGreaterEqual(ttl, expected - ABSOLUTE_EXPIRE_CLOCK_SLACK_SECONDS)
        self.assertLessEqual(ttl, expected + ABSOLUTE_EXPIRE_CLOCK_SLACK_SECONDS)

    def test_an_expire_under_one_second_fails_the_call_and_stores_nothing(self):
        self.widget_catalogue.names[14] = 'acme'
        with self.assertRaises(ValueError):
            self.widget_catalogue.get_blink(14)
        self.assertIsNone(self._server_ttl('memcached_widget_blink_14'))

    def test_an_expired_entry_is_recomputed_and_stored_again(self):
        self.widget_catalogue.names[15] = 'acme'
        self.assertEqual('acme', self.widget_catalogue.get_short(15))
        self.widget_catalogue.names[15] = 'widget'
        sleep(0.5)
        self.assertEqual('acme', self.widget_catalogue.get_short(15))
        sleep(1.7)
        self.assertEqual('widget', self.widget_catalogue.get_short(15))
        self.assertEqual('widget', self._stored('memcached_widget_short_15'))
        self.assertEqual(2, self.widget_catalogue.calls)

    def test_a_none_result_is_never_stored(self):
        self.widget_catalogue.names[16] = None
        self.assertIsNone(self.widget_catalogue.get(16))
        self.assertIsNone(self.widget_catalogue.get(16))
        self.assertIsNone(self._server_ttl('memcached_widget_16'))
        self.assertEqual(2, self.widget_catalogue.calls)

    def test_cache_empty_result_false_stores_no_empty_result(self):
        for widget_id, (label, result) in enumerate(EMPTY_RESULTS.items(), start=200):
            with self.subTest(label):
                self.widget_catalogue.names[widget_id] = result
                calls_before = self.widget_catalogue.calls
                self.assertEqual(result, self.widget_catalogue.get_non_empty(widget_id))
                self.assertEqual(result, self.widget_catalogue.get_non_empty(widget_id))
                self.assertIsNone(self._server_ttl('memcached_widget_non_empty_{}'.format(widget_id)))
                self.assertEqual(calls_before + 2, self.widget_catalogue.calls)

    def test_cache_empty_result_false_still_stores_a_non_empty_result(self):
        self.widget_catalogue.names[17] = 'acme'
        self.widget_catalogue.get_non_empty(17)
        self.widget_catalogue.get_non_empty(17)
        self.assertEqual('acme', self._stored('memcached_widget_non_empty_17'))
        self.assertEqual(1, self.widget_catalogue.calls)

    def test_a_result_of_a_type_memcached_cannot_hold_fails_the_call_and_stores_nothing(self):
        for widget_id, result in ((18, {'acme', 'widget'}), (19, 1.5), (20, ('acme', 1))):
            with self.subTest(type(result).__name__):
                self.widget_catalogue.names[widget_id] = result
                with self.assertRaises(ValueError):
                    self.widget_catalogue.get(widget_id)
                self.assertIsNone(self._server_ttl('memcached_widget_{}'.format(widget_id)))

    def test_a_result_over_the_item_limit_fails_the_call_and_stores_nothing(self):
        self.widget_catalogue.names[21] = 'a' * (ITEM_LIMIT_BYTES + 10)
        with self.assertRaises(RuntimeError):
            self.widget_catalogue.get(21)
        self.assertIsNone(self._server_ttl('memcached_widget_21'))

    def test_an_unreachable_memcached_fails_the_call_when_it_stores(self):
        self._use_handler(self._unreachable_cache_handler())
        self.widget_catalogue.names[22] = 'acme'
        with self.assertRaises(RuntimeError):
            self.widget_catalogue.get(22)
        self.assertEqual(1, self.widget_catalogue.calls)  # the read is a miss, so the function ran; the store raised

    def test_an_exception_in_the_function_stores_nothing(self):
        with self.assertRaises(KeyError):
            self.widget_catalogue.get(23)  # no name for 23
        self.assertIsNone(self._server_ttl('memcached_widget_23'))
        self.widget_catalogue.names[23] = 'acme'
        self.assertEqual('acme', self.widget_catalogue.get(23))
        self.assertEqual('acme', self._stored('memcached_widget_23'))

    def test_invalidate_clears_the_key_and_the_next_read_recomputes(self):
        self.widget_catalogue.names[24] = 'acme'
        self.assertEqual('acme', self.widget_catalogue.get(24))
        self.widget_catalogue.rename(24, 'widget')
        self.assertIsNone(self._server_ttl('memcached_widget_24'))
        self.assertEqual('widget', self.widget_catalogue.get(24))
        self.assertEqual('widget', self._stored('memcached_widget_24'))
        self.assertEqual(2, self.widget_catalogue.calls)

    def test_invalidate_clears_only_its_own_key(self):
        self.widget_catalogue.names[25] = 'acme'
        self.widget_catalogue.names[26] = 'widget'
        self.widget_catalogue.get(25)
        self.widget_catalogue.get(26)
        self.widget_catalogue.get_fresh(25)
        self.widget_catalogue.rename(25, 'reviewer')
        self.assertIsNone(self._server_ttl('memcached_widget_25'))
        self.assertEqual('widget', self._stored('memcached_widget_26'))
        self.assertEqual('acme', self._stored('memcached_widget_fresh_25'))

    def test_invalidate_of_a_key_never_cached_does_nothing(self):
        self.widget_catalogue.names[27] = 'acme'
        self.widget_catalogue.get(27)
        self.widget_catalogue.rename(28, 'widget')
        self.assertEqual('acme', self._stored('memcached_widget_27'))

    def test_an_invalidation_that_raises_keeps_the_cached_value(self):
        self.widget_catalogue.names[29] = 'acme'
        self.widget_catalogue.get(29)
        with self.assertRaises(RuntimeError):
            self.widget_catalogue.fail_to_rename(29, 'widget')
        self.assertEqual('acme', self._stored('memcached_widget_29'))
        self.assertEqual('acme', self.widget_catalogue.get(29))
        self.assertEqual(1, self.widget_catalogue.calls)

    def test_spaces_in_an_argument_become_underscores_so_both_spellings_share_one_entry(self):
        self.widget_catalogue.names['acme widget'] = 'first'
        self.widget_catalogue.names['acme_widget'] = 'second'
        self.assertEqual('first', self.widget_catalogue.get_by_name('acme widget'))
        self.assertEqual('first', self._stored('memcached_widget_name_acme_widget'))
        self.assertEqual('first', self.widget_catalogue.get_by_name('acme_widget'))  # the other spelling's value
        self.assertEqual(1, self.widget_catalogue.calls)

    def test_every_falsy_argument_renders_one_placeholder_so_all_share_one_entry(self):
        self.widget_catalogue.names[0] = 'zero'
        self.widget_catalogue.names[None] = 'none'
        self.assertEqual('zero', self.widget_catalogue.get(0))
        self.assertEqual('zero', self._stored('memcached_widget_!Ewidget_idE!'))
        self.assertEqual('zero', self.widget_catalogue.get(None))  # 0's value, not None's
        self.assertEqual(1, self.widget_catalogue.calls)

    def test_an_argument_making_a_refused_key_fails_the_call_before_the_function_runs(self):
        for label, name in NAMES_MAKING_A_REFUSED_KEY.items():
            with self.subTest(label):
                self.widget_catalogue.names[name] = label
                with self.assertRaises(Client.MemcachedKeyError):
                    self.widget_catalogue.get_by_name(name)
        self.assertEqual(0, self.widget_catalogue.calls)
        self.assertIsNone(self.memcached_client.get('memcached_widget_name_acme_widget'))  # never rewritten

    def test_a_key_is_cut_to_max_key_length_so_labels_alike_up_to_it_share_one_entry(self):
        long_label = 'acme-widget-reviewer-one'
        other_long_label = 'acme-widget-reviewer-two'
        self.widget_catalogue.names[long_label] = 'first'
        self.widget_catalogue.names[other_long_label] = 'second'
        self.assertEqual('first', self.widget_catalogue.get_by_label(long_label))
        self.assertEqual('first', self._stored('memcached_widget_label_acme-widget'))
        self.assertEqual('first', self.widget_catalogue.get_by_label(other_long_label))
        self.assertEqual(LABEL_KEY_LENGTH, len('memcached_widget_label_acme-widget'))

    def test_a_read_inside_a_transaction_neither_reads_nor_fills_memcached(self):
        self.widget_catalogue.names[30] = 'acme'
        self.widget_catalogue.get(30)
        self.widget_catalogue.names[30] = 'widget'
        self.widget_catalogue.names[31] = 'reviewer'
        self.assertEqual('widget', self.widget_catalogue.get_in_transaction(30))
        self.assertEqual('reviewer', self.widget_catalogue.get_in_transaction(31))
        self.assertEqual('acme', self._stored('memcached_widget_30'))
        self.assertFalse(self._is_stored('memcached_widget_31'))

    def test_an_invalidation_inside_a_transaction_clears_memcached_only_after_the_commit(self):
        self.widget_catalogue.names[32] = 'acme'
        self.widget_catalogue.get(32)
        stored_before_the_commit = self.widget_catalogue.rename_in_transaction(32, 'widget', self.memcached_client)
        self.assertTrue(stored_before_the_commit)
        self.assertFalse(self._is_stored('memcached_widget_32'))
        self.assertEqual('widget', self.widget_catalogue.get(32))

    def test_an_invalidation_inside_a_rolled_back_transaction_keeps_the_cached_value(self):
        self.widget_catalogue.names[33] = 'acme'
        self.widget_catalogue.get(33)
        with self.assertRaises(RuntimeError):
            self.widget_catalogue.rename_then_roll_back(33, 'widget')
        self.assertEqual('acme', self._stored('memcached_widget_33'))
        self.assertEqual(NO_EXPIRY_TTL, self._server_ttl('memcached_widget_33'))

    def test_concurrent_reads_of_different_keys_never_get_each_others_results(self):
        for widget_id in range(THREAD_COUNT):
            self.widget_catalogue.names[widget_id + 300] = {'widget': widget_id + 300}

        def read_twice(widget_id: int) -> list:
            reads = [self.widget_catalogue.get(widget_id), self.widget_catalogue.get(widget_id)]
            # the client keeps one connection per thread
            CoreLib.cache_registry.get(CACHE_HANDLER_NAME).memcached_client.disconnect_all()
            return reads

        widget_ids = [widget_id + 300 for widget_id in range(THREAD_COUNT)]
        with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
            reads = list(executor.map(read_twice, widget_ids))
        self.assertEqual([[{'widget': widget_id}] * 2 for widget_id in widget_ids], reads)
        for widget_id in widget_ids:
            self.assertEqual({'widget': widget_id}, self._stored('memcached_widget_{}'.format(widget_id)))
