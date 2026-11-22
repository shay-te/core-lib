"""`CacheHandlerRedis` stores, expires and removes values on a real Redis server, exactly and only as asked.

Runs only when `CORE_LIB_TEST_REDIS_URL` names a THROWAWAY Redis (`redis://127.0.0.1:56379/0`); skipped
otherwise. Every test empties that server (`flush_all` is `FLUSHALL`), so never point it at one holding data.
"""
import enum
import json
import os
import socket
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from decimal import Decimal
from time import sleep
from urllib.parse import urlparse, urlunparse

import redis

from core_lib.cache.cache_handler_redis import CacheHandlerRedis

REDIS_URL = os.environ.get('CORE_LIB_TEST_REDIS_URL')
NO_EXPIRY_TTL = -1  # the TTL Redis reports for a key stored with no expiry
ABSENT_KEY_TTL = -2  # the TTL Redis reports for a key that does not exist
TEN_MINUTES = timedelta(minutes=10)
ONE_YEAR = timedelta(days=365)
REFUSED_MESSAGE = 'result must be of type `dict`, `list`, `int` or `str`. got `{}`'
SUPPORTED_VALUES = {
    'dict': {'name': 'acme', 'tags': ['widget', 'reviewer'], 'count': 2},
    'dict_in_unsorted_key_order': {'zeta': 1, 'alpha': 2, 'mid': 3},
    'dict_holding_null': {'owner': None},
    'list': ['acme', 1, {'nested': True}, None],
    'deeply_nested': {'level': [{'level': [{'level': ['acme']}]}]},
    'list_of_floats': [0.1 + 0.2, 1.0, -2.5],
    'int': 42,
    'negative_int': -7,
    'int_past_64_bits': 2 ** 100,
    'true': True,
    'false': False,
    'str': 'acme widget',
    'unicode_str': 'acme ✓ ש \U0001F600',
    'str_that_looks_like_json': '{"name": "acme"}',
    'str_null': 'null',
    'str_with_leading_zeros': '007',
}
EMPTY_VALUES = {'zero': 0, 'empty_str': '', 'empty_list': [], 'empty_dict': {}}
REFUSED_VALUES = {
    'set': ({'acme'}, "<class 'set'>"),
    'frozenset': (frozenset({'acme'}), "<class 'frozenset'>"),
    'tuple': (('acme', 1), "<class 'tuple'>"),
    'float': (1.5, "<class 'float'>"),
    'none': (None, "<class 'NoneType'>"),
    'bytes': (b'acme', "<class 'bytes'>"),
    'decimal': (Decimal('1.5'), "<class 'decimal.Decimal'>"),
    'timedelta': (timedelta(days=1), "<class 'datetime.timedelta'>"),
    'object': (object(), "<class 'object'>"),
}
MORE_THAN_ZERO_MESSAGE = 'expire must be more than 0. got `{!r}`'
WHOLE_MILLISECONDS_MESSAGE = 'expire must be a whole number of milliseconds. got `{!r}`'
KEYS_MEMCACHED_REFUSES = {  # Redis keys are binary-safe: Redis keeps every one of these, exactly as given
    'space': 'acme widget',
    'leading_space': ' widget',
    'tab': 'acme\twidget',
    'newline': 'acme\nwidget',
    'carriage_return': 'acme\rwidget',
    'null_character': 'acme\x00widget',
    'delete_character': 'acme\x7fwidget',
    'empty': '',
    'over_250_bytes': 'acme_' + 'k' * 246,
    'non_ascii_over_250_bytes': '\u2713' * 84,
    'ascii_5000_bytes': 'k' * 5000,
}
WRONG_EXPIRES = {  # a time Redis cannot keep exactly: refused, never rounded or cut
    'zero': (timedelta(0), MORE_THAN_ZERO_MESSAGE),
    'minus_one_microsecond': (timedelta(microseconds=-1), MORE_THAN_ZERO_MESSAGE),
    'minus_five_seconds': (timedelta(seconds=-5), MORE_THAN_ZERO_MESSAGE),
    'one_microsecond': (timedelta(microseconds=1), WHOLE_MILLISECONDS_MESSAGE),
    'a_microsecond_short_of_a_millisecond': (timedelta(microseconds=999), WHOLE_MILLISECONDS_MESSAGE),
    'a_millisecond_and_a_microsecond': (timedelta(milliseconds=1, microseconds=1), WHOLE_MILLISECONDS_MESSAGE),
    'thirty_one_days_and_a_microsecond': (timedelta(days=31, microseconds=1), WHOLE_MILLISECONDS_MESSAGE),
}
UNSERIALISABLE_NESTED_VALUES = {
    'set_in_dict': {'tags': {'acme'}},
    'object_in_list': ['acme', object()],
    'datetime_in_dict': {'created_at': datetime(2026, 1, 2, 3, 4, 5)},
}
THREAD_COUNT = 16
ROUNDS_PER_THREAD = 50


class WidgetKind(enum.IntEnum):
    ALPHA = 1


class WidgetLabel(str, enum.Enum):
    ACME = 'acme'


@unittest.skipUnless(REDIS_URL, 'needs a throwaway Redis server: set CORE_LIB_TEST_REDIS_URL')
class TestCacheHandlerRedis(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.redis_client = redis.from_url(REDIS_URL)  # the test's own view of what the server holds
        cls.cache_handler = CacheHandlerRedis(REDIS_URL)

    @classmethod
    def tearDownClass(cls):
        cls.redis_client.flushall()
        cls.redis_client.close()

    def setUp(self):
        self.redis_client.flushall()

    def _stored(self, key: str):
        return json.loads(self.redis_client.get(key))

    def _assert_reads_back_exactly(self, expected, actual):
        # `==` alone takes 42 == 42.0 == True and ignores dict order; the JSON text tells all three apart
        self.assertEqual(expected, actual)
        self.assertEqual(json.dumps(expected), json.dumps(actual))

    def _other_database_url(self) -> str:
        database = self.redis_client.connection_pool.connection_kwargs.get('db', 0)
        return urlunparse(urlparse(REDIS_URL)._replace(path='/{}'.format((database + 1) % 16)))

    def test_set_without_expire_stores_every_supported_value_with_no_expiry(self):
        for label, value in {**SUPPORTED_VALUES, **EMPTY_VALUES}.items():
            with self.subTest(label):
                key = 'widget_{}'.format(label)
                self.cache_handler.set(key, value, None)
                self._assert_reads_back_exactly(value, self._stored(key))
                self.assertEqual(NO_EXPIRY_TTL, self.redis_client.ttl(key))
                self._assert_reads_back_exactly(value, self.cache_handler.get(key))

    def test_set_with_expire_stores_every_supported_value_with_that_expiry(self):
        for label, value in {**SUPPORTED_VALUES, **EMPTY_VALUES}.items():
            with self.subTest(label):
                key = 'widget_{}'.format(label)
                self.cache_handler.set(key, value, TEN_MINUTES)
                self._assert_reads_back_exactly(value, self._stored(key))
                self.assertIn(self.redis_client.ttl(key), (599, 600))
                self._assert_reads_back_exactly(value, self.cache_handler.get(key))

    def test_empty_values_read_back_as_themselves_never_as_a_miss(self):
        for label, value in EMPTY_VALUES.items():
            with self.subTest(label):
                key = 'widget_{}'.format(label)
                self.cache_handler.set(key, value, None)
                read_back = self.cache_handler.get(key)
                self.assertIsNotNone(read_back)
                self.assertEqual((type(value), value), (type(read_back), read_back))

    def test_a_one_year_expire_is_kept_in_full(self):
        self.cache_handler.set('widget_yearly', 'acme', ONE_YEAR)
        self.assertIn(self.redis_client.ttl('widget_yearly'), (31535999, 31536000))

    def test_a_one_second_expire_neither_ends_early_nor_late(self):
        self.cache_handler.set('widget_short', {'name': 'acme'}, timedelta(seconds=1))
        remaining_ms = self.redis_client.pttl('widget_short')
        self.assertGreater(remaining_ms, 800)
        self.assertLessEqual(remaining_ms, 1000)
        sleep(0.5)
        self.assertEqual({'name': 'acme'}, self.cache_handler.get('widget_short'))
        sleep(0.7)
        self.assertIsNone(self.cache_handler.get('widget_short'))
        self.assertEqual(ABSENT_KEY_TTL, self.redis_client.ttl('widget_short'))

    def test_an_expire_with_a_part_of_a_second_is_kept_to_the_millisecond(self):
        self.cache_handler.set('widget_blink', 'acme', timedelta(milliseconds=600))
        self.cache_handler.set('widget_second', 'acme', timedelta(seconds=1, milliseconds=500))
        self.assertGreater(self.redis_client.pttl('widget_blink'), 500)
        self.assertLessEqual(self.redis_client.pttl('widget_blink'), 600)
        self.assertGreater(self.redis_client.pttl('widget_second'), 1400)
        self.assertLessEqual(self.redis_client.pttl('widget_second'), 1500)
        sleep(0.3)
        self.assertEqual(['acme', 'acme'], [self.cache_handler.get('widget_blink'),
                                            self.cache_handler.get('widget_second')])
        sleep(0.5)
        self.assertEqual([None, 'acme'], [self.cache_handler.get('widget_blink'),
                                          self.cache_handler.get('widget_second')])
        sleep(0.9)
        self.assertIsNone(self.cache_handler.get('widget_second'))

    def test_a_one_millisecond_expire_is_sent_as_one_millisecond(self):
        self.cache_handler.set('widget_millisecond', 'acme', timedelta(milliseconds=1))
        sleep(0.05)
        self.assertIsNone(self.cache_handler.get('widget_millisecond'))
        self.assertEqual(ABSENT_KEY_TTL, self.redis_client.ttl('widget_millisecond'))

    def test_an_expire_the_cache_cannot_keep_exactly_raises_and_keeps_the_stored_value(self):
        for label, (expire, message) in WRONG_EXPIRES.items():
            with self.subTest(label):
                key = 'widget_{}'.format(label)
                self.cache_handler.set(key, 'acme', TEN_MINUTES)
                with self.assertRaises(ValueError) as context:
                    self.cache_handler.set(key, 'widget', expire)
                self.assertEqual(message.format(expire), str(context.exception))
                self.assertEqual('acme', self.cache_handler.get(key))
                self.assertIn(self.redis_client.ttl(key), (599, 600))

    def test_an_expire_the_cache_cannot_keep_exactly_never_creates_the_key(self):
        for label, (expire, _) in WRONG_EXPIRES.items():
            with self.subTest(label):
                key = 'widget_new_{}'.format(label)
                with self.assertRaises(ValueError):
                    self.cache_handler.set(key, 'acme', expire)
                self.assertIsNone(self.cache_handler.get(key))

    def test_dict_int_keys_come_back_as_strings(self):
        self.cache_handler.set('widget_by_id', {1: 'acme', 2: 'widget'}, None)
        self.assertEqual({'1': 'acme', '2': 'widget'}, self.cache_handler.get('widget_by_id'))

    def test_tuples_inside_a_value_come_back_as_lists(self):
        self.cache_handler.set('widget_pair', {'pair': ('acme', 1)}, None)
        self._assert_reads_back_exactly({'pair': ['acme', 1]}, self.cache_handler.get('widget_pair'))

    def test_enum_members_come_back_as_their_plain_values(self):
        self.cache_handler.set('widget_kind', WidgetKind.ALPHA, None)
        self.cache_handler.set('widget_label', WidgetLabel.ACME, None)
        kind = self.cache_handler.get('widget_kind')
        label = self.cache_handler.get('widget_label')
        self.assertEqual((int, 1), (type(kind), kind))
        self.assertEqual((str, 'acme'), (type(label), label))

    def test_large_values_round_trip_whole(self):
        large_str = 'acme-widget-' * 100_000
        large_list = [{'position': i, 'name': 'widget'} for i in range(10_000)]
        self.cache_handler.set('widget_large_str', large_str, None)
        self.cache_handler.set('widget_large_list', large_list, None)
        self.assertEqual(large_str, self.cache_handler.get('widget_large_str'))
        self.assertEqual(large_list, self.cache_handler.get('widget_large_list'))

    def test_set_refuses_every_unsupported_type_and_keeps_the_stored_value(self):
        for label, (value, type_text) in REFUSED_VALUES.items():
            with self.subTest(label):
                key = 'widget_{}'.format(label)
                self.cache_handler.set(key, 'acme', TEN_MINUTES)
                with self.assertRaises(ValueError) as context:
                    self.cache_handler.set(key, value, None)
                self.assertEqual(REFUSED_MESSAGE.format(type_text), str(context.exception))
                self.assertEqual('acme', self.cache_handler.get(key))
                self.assertIn(self.redis_client.ttl(key), (599, 600))

    def test_set_refuses_an_unsupported_type_without_creating_the_key(self):
        with self.assertRaises(ValueError):
            self.cache_handler.set('widget_never_created', {'acme'}, None)
        self.assertEqual(0, self.redis_client.exists('widget_never_created'))

    def test_a_value_holding_something_json_cannot_encode_raises_and_keeps_the_stored_value(self):
        for label, value in UNSERIALISABLE_NESTED_VALUES.items():
            with self.subTest(label):
                key = 'widget_{}'.format(label)
                self.cache_handler.set(key, 'acme', None)
                with self.assertRaises(TypeError):
                    self.cache_handler.set(key, value, None)
                self.assertEqual('acme', self.cache_handler.get(key))

    def test_get_of_an_absent_key_returns_none(self):
        self.assertIsNone(self.cache_handler.get('widget_never_stored'))

    def test_set_replaces_the_value_and_drops_the_old_expiry(self):
        self.cache_handler.set('widget_replaced', {'name': 'acme'}, TEN_MINUTES)
        self.cache_handler.set('widget_replaced', 7, None)
        self._assert_reads_back_exactly(7, self.cache_handler.get('widget_replaced'))
        self.assertEqual(NO_EXPIRY_TTL, self.redis_client.ttl('widget_replaced'))

    def test_set_replaces_the_value_and_adds_an_expiry(self):
        self.cache_handler.set('widget_replaced', 'acme', None)
        self.cache_handler.set('widget_replaced', ['widget'], TEN_MINUTES)
        self.assertEqual(['widget'], self.cache_handler.get('widget_replaced'))
        self.assertIn(self.redis_client.ttl('widget_replaced'), (599, 600))

    def test_every_key_memcached_refuses_is_kept_exactly_as_given(self):
        for label, key in KEYS_MEMCACHED_REFUSES.items():
            with self.subTest(label):
                self.cache_handler.set(key, label, None)
        self.assertEqual(len(KEYS_MEMCACHED_REFUSES), self.redis_client.dbsize())
        for label, key in KEYS_MEMCACHED_REFUSES.items():
            with self.subTest(label):
                self.assertEqual(label, self.cache_handler.get(key))
                self.assertEqual(label, self._stored(key))  # under the very key given, never a rewritten one
                self.cache_handler.delete(key)
                self.assertIsNone(self.cache_handler.get(key))
        self.assertEqual(0, self.redis_client.dbsize())

    def test_keys_are_otherwise_matched_exactly(self):
        keys = ['widget', 'Widget', 'widget_\u2713', 'widget-1', 'widget.1', 'acme_widget']
        for position, key in enumerate(keys):
            self.cache_handler.set(key, position, None)
        for position, key in enumerate(keys):
            with self.subTest(key):
                self.assertEqual(position, self.cache_handler.get(key))
                self.assertEqual(position, self._stored(key))

    def test_a_key_of_exactly_250_bytes_is_kept_whole(self):
        for label, key in (('ascii', 'k' * 250), ('non_ascii', '\u05e9' * 125)):  # 125 two-byte characters
            with self.subTest(label):
                self.cache_handler.set(key, label, None)
                self.assertEqual(label, self.cache_handler.get(key))
                self.assertEqual(label, self._stored(key))

    def test_delete_removes_only_that_key(self):
        self.cache_handler.set('widget_deleted', 'acme', None)
        self.cache_handler.set('widget_kept', 'widget', None)
        self.cache_handler.delete('widget_deleted')
        self.assertIsNone(self.cache_handler.get('widget_deleted'))
        self.assertEqual(0, self.redis_client.exists('widget_deleted'))
        self.assertEqual('widget', self.cache_handler.get('widget_kept'))

    def test_delete_removes_a_key_that_has_an_expiry(self):
        self.cache_handler.set('widget_expiring', 'acme', TEN_MINUTES)
        self.cache_handler.delete('widget_expiring')
        self.assertEqual(ABSENT_KEY_TTL, self.redis_client.ttl('widget_expiring'))

    def test_delete_of_an_absent_key_does_nothing(self):
        self.cache_handler.set('widget_kept', 'widget', None)
        self.cache_handler.delete('widget_never_stored')
        self.assertEqual('widget', self.cache_handler.get('widget_kept'))
        self.assertEqual(1, self.redis_client.dbsize())

    def test_a_deleted_key_can_be_stored_again(self):
        self.cache_handler.set('widget_reused', 'acme', TEN_MINUTES)
        self.cache_handler.delete('widget_reused')
        self.cache_handler.set('widget_reused', 'widget', None)
        self.assertEqual('widget', self.cache_handler.get('widget_reused'))
        self.assertEqual(NO_EXPIRY_TTL, self.redis_client.ttl('widget_reused'))

    def test_flush_all_empties_the_cache_and_the_handler_keeps_working(self):
        self.cache_handler.set('widget_forever', {'name': 'acme'}, None)
        self.cache_handler.set('widget_expiring', ['widget'], TEN_MINUTES)
        self.cache_handler.flush_all()
        self.assertIsNone(self.cache_handler.get('widget_forever'))
        self.assertIsNone(self.cache_handler.get('widget_expiring'))
        self.assertEqual(0, self.redis_client.dbsize())
        self.cache_handler.set('widget_after_flush', 'acme', None)
        self.assertEqual('acme', self.cache_handler.get('widget_after_flush'))

    def test_flush_all_empties_every_database_of_the_server_not_only_its_own(self):
        other_cache_handler = CacheHandlerRedis(self._other_database_url())
        self.cache_handler.set('widget_own_database', 'acme', None)
        other_cache_handler.set('widget_other_database', 'widget', None)
        other_cache_handler.flush_all()  # FLUSHALL: a Redis shared with other data loses it too
        self.assertIsNone(self.cache_handler.get('widget_own_database'))
        self.assertIsNone(other_cache_handler.get('widget_other_database'))

    def test_flush_all_of_an_empty_cache_does_nothing(self):
        self.cache_handler.flush_all()
        self.assertEqual(0, self.redis_client.dbsize())

    def test_handlers_on_two_databases_never_see_each_others_values(self):
        other_cache_handler = CacheHandlerRedis(self._other_database_url())
        self.cache_handler.set('widget_shared_name', 'acme', None)
        other_cache_handler.set('widget_shared_name', 'widget', None)
        other_cache_handler.set('widget_other_only', 'reviewer', None)
        self.assertEqual('acme', self.cache_handler.get('widget_shared_name'))
        self.assertEqual('widget', other_cache_handler.get('widget_shared_name'))
        self.assertIsNone(self.cache_handler.get('widget_other_only'))
        other_cache_handler.delete('widget_shared_name')
        self.assertEqual('acme', self.cache_handler.get('widget_shared_name'))
        self.assertEqual(1, self.redis_client.dbsize())

    def test_two_handlers_on_one_url_share_their_values(self):
        second_cache_handler = CacheHandlerRedis(REDIS_URL)  # another process pointed at the same cache
        self.cache_handler.set('widget_shared', {'name': 'acme'}, None)
        self.assertEqual({'name': 'acme'}, second_cache_handler.get('widget_shared'))
        second_cache_handler.delete('widget_shared')
        self.assertIsNone(self.cache_handler.get('widget_shared'))

    def test_concurrent_threads_never_read_each_others_values(self):
        def store_and_read(thread_number: int) -> list:
            mismatches = []
            key = 'widget_thread_{}'.format(thread_number)
            for round_number in range(ROUNDS_PER_THREAD):
                value = {'thread': thread_number, 'round': round_number}
                self.cache_handler.set(key, value, TEN_MINUTES)
                read_back = self.cache_handler.get(key)
                if read_back != value:
                    mismatches.append(read_back)
            return mismatches

        with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
            mismatches = [mismatch for found in executor.map(store_and_read, range(THREAD_COUNT)) for mismatch in found]
        self.assertEqual([], mismatches)
        self.assertEqual(THREAD_COUNT, self.redis_client.dbsize())
        self.assertEqual({'thread': 3, 'round': ROUNDS_PER_THREAD - 1}, self.cache_handler.get('widget_thread_3'))

    def test_an_unreachable_server_raises_on_every_operation_never_answers_a_miss(self):
        with socket.socket() as unused_port_socket:
            unused_port_socket.bind(('127.0.0.1', 0))
            unused_port = unused_port_socket.getsockname()[1]
        unreachable_cache_handler = CacheHandlerRedis('redis://127.0.0.1:{}/0'.format(unused_port))  # connects lazily
        operations = {
            'get': lambda: unreachable_cache_handler.get('widget'),
            'set': lambda: unreachable_cache_handler.set('widget', 'acme', None),
            'delete': lambda: unreachable_cache_handler.delete('widget'),
            'flush_all': unreachable_cache_handler.flush_all,
        }
        for label, operation in operations.items():
            with self.subTest(label), self.assertRaises(redis.exceptions.ConnectionError):
                operation()

    def test_a_url_with_an_unknown_scheme_is_refused_at_construction(self):
        with self.assertRaises(ValueError):
            CacheHandlerRedis('http://127.0.0.1:6379/0')
