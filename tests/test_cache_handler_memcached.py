"""`CacheHandlerMemcached` stores, expires and removes values on a real memcached server, exactly and only as asked.

Runs only when `CORE_LIB_TEST_MEMCACHED_URL` names a THROWAWAY memcached (`127.0.0.1:51211`); skipped otherwise.
Every test empties that server, so never point it at one holding data. memcached's clock ticks once a second, so an
item asked to live N seconds lives between N-1 and N seconds, and a TTL read right after a store can be one less.
"""
import enum
import json
import os
import socket
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from decimal import Decimal
from time import sleep

from memcache import Client

from core_lib.cache.cache_handler_memcached import CacheHandlerMemcached

MEMCACHED_URL = os.environ.get('CORE_LIB_TEST_MEMCACHED_URL')
NOT_STORED_MESSAGE = 'memcached did not store a value of {} bytes'
NO_EXPIRY_TTL = -1  # the TTL memcached reports for an item stored with no expiry
TEN_MINUTES = timedelta(minutes=10)
THIRTY_DAYS_SECONDS = 2_592_000
ITEM_LIMIT_BYTES = 1024 * 1024
# over 30 days memcached takes a Unix time and reads it against its OWN clock, which can lag the client's (a
# Docker VM that slept lags by minutes): such a TTL reads longer by that lag, measured from `stats time`
ABSOLUTE_EXPIRE_CLOCK_SLACK_SECONDS = 2  # the once-a-second tick of both clocks
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
UNSERIALISABLE_NESTED_VALUES = {
    'set_in_dict': {'tags': {'acme'}},
    'object_in_list': ['acme', object()],
    'datetime_in_dict': {'created_at': datetime(2026, 1, 2, 3, 4, 5)},
}
MORE_THAN_ZERO_MESSAGE = 'expire must be more than 0. got `{!r}`'
WHOLE_SECONDS_MESSAGE = 'expire must be a whole number of seconds. got `{!r}`'
WRONG_EXPIRES = {  # a time memcached cannot keep exactly: refused, never rounded or cut
    'zero': (timedelta(0), MORE_THAN_ZERO_MESSAGE),
    'minus_one_microsecond': (timedelta(microseconds=-1), MORE_THAN_ZERO_MESSAGE),
    'minus_five_seconds': (timedelta(seconds=-5), MORE_THAN_ZERO_MESSAGE),
    'one_millisecond': (timedelta(milliseconds=1), WHOLE_SECONDS_MESSAGE),
    'half_a_second': (timedelta(milliseconds=500), WHOLE_SECONDS_MESSAGE),
    'a_microsecond_short_of_one_second': (timedelta(seconds=1, microseconds=-1), WHOLE_SECONDS_MESSAGE),
    'one_and_nine_tenths_seconds': (timedelta(seconds=1, milliseconds=900), WHOLE_SECONDS_MESSAGE),
    'a_minute_and_a_microsecond': (timedelta(minutes=1, microseconds=1), WHOLE_SECONDS_MESSAGE),
    'thirty_one_days_and_a_millisecond': (timedelta(days=31, milliseconds=1), WHOLE_SECONDS_MESSAGE),
}
LONG_EXPIRES = {
    'thirty_days_and_a_second': timedelta(days=30, seconds=1),
    'thirty_one_days': timedelta(days=31),
    'one_year': timedelta(days=365),
}
REFUSED_KEYS = {  # memcached's own key limits: python-memcached raises its own error, counting bytes
    'space': ('acme widget', Client.MemcachedKeyCharacterError),
    'leading_space': (' widget', Client.MemcachedKeyCharacterError),
    'tab': ('acme\twidget', Client.MemcachedKeyCharacterError),
    'newline': ('acme\nwidget', Client.MemcachedKeyCharacterError),
    'carriage_return': ('acme\rwidget', Client.MemcachedKeyCharacterError),
    'null_character': ('acme\x00widget', Client.MemcachedKeyCharacterError),
    'delete_character': ('acme\x7fwidget', Client.MemcachedKeyCharacterError),
    'empty': ('', Client.MemcachedKeyCharacterError),
    'over_250_bytes': ('acme_' + 'k' * 246, Client.MemcachedKeyLengthError),
    'non_ascii_over_250_bytes': ('\u2713' * 84, Client.MemcachedKeyLengthError),
}
THREAD_COUNT = 16
ROUNDS_PER_THREAD = 50


class WidgetKind(enum.IntEnum):
    ALPHA = 1


class WidgetLabel(str, enum.Enum):
    ACME = 'acme'


@unittest.skipUnless(MEMCACHED_URL, 'needs a throwaway memcached server: set CORE_LIB_TEST_MEMCACHED_URL')
class TestCacheHandlerMemcached(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.memcached_client = Client([MEMCACHED_URL])  # the test's own view of what the server holds
        cls.cache_handler = CacheHandlerMemcached(MEMCACHED_URL)

    @classmethod
    def tearDownClass(cls):
        cls.memcached_client.flush_all()
        cls.memcached_client.disconnect_all()
        cls.cache_handler.memcached_client.disconnect_all()

    def setUp(self):
        self.memcached_client.flush_all()

    def _stored(self, key: str):
        return json.loads(self.memcached_client.get(key))

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

    def _assert_reads_back_exactly(self, expected, actual):
        # `==` alone takes 42 == 42.0 == True and ignores dict order; the JSON text tells all three apart
        self.assertEqual(expected, actual)
        self.assertEqual(json.dumps(expected), json.dumps(actual))

    def _unreachable_cache_handler(self) -> CacheHandlerMemcached:
        with socket.socket() as unused_port_socket:
            unused_port_socket.bind(('127.0.0.1', 0))
            unused_port = unused_port_socket.getsockname()[1]
        return CacheHandlerMemcached('127.0.0.1:{}'.format(unused_port))

    def test_set_without_expire_stores_every_supported_value_with_no_expiry(self):
        for label, value in {**SUPPORTED_VALUES, **EMPTY_VALUES}.items():
            with self.subTest(label):
                key = 'widget_{}'.format(label)
                self.cache_handler.set(key, value, None)
                self._assert_reads_back_exactly(value, self._stored(key))
                self.assertEqual(NO_EXPIRY_TTL, self._server_ttl(key))
                self._assert_reads_back_exactly(value, self.cache_handler.get(key))

    def test_set_with_expire_stores_every_supported_value_with_that_expiry(self):
        for label, value in {**SUPPORTED_VALUES, **EMPTY_VALUES}.items():
            with self.subTest(label):
                key = 'widget_{}'.format(label)
                self.cache_handler.set(key, value, TEN_MINUTES)
                self._assert_reads_back_exactly(value, self._stored(key))
                self.assertIn(self._server_ttl(key), (599, 600))
                self._assert_reads_back_exactly(value, self.cache_handler.get(key))

    def test_empty_values_read_back_as_themselves_never_as_a_miss(self):
        for label, value in EMPTY_VALUES.items():
            with self.subTest(label):
                key = 'widget_{}'.format(label)
                self.cache_handler.set(key, value, None)
                read_back = self.cache_handler.get(key)
                self.assertIsNotNone(read_back)
                self.assertEqual((type(value), value), (type(read_back), read_back))

    def test_a_two_second_expire_lives_more_than_one_second_and_at_most_two(self):
        self.cache_handler.set('widget_short', {'name': 'acme'}, timedelta(seconds=2))
        self.assertIn(self._server_ttl('widget_short'), (1, 2))
        sleep(0.5)
        self.assertEqual({'name': 'acme'}, self.cache_handler.get('widget_short'))
        sleep(1.7)
        self.assertIsNone(self.cache_handler.get('widget_short'))
        self.assertIsNone(self._server_ttl('widget_short'))

    def test_an_expire_the_cache_cannot_keep_exactly_raises_and_keeps_the_stored_value(self):
        for label, (expire, message) in WRONG_EXPIRES.items():
            with self.subTest(label):
                key = 'widget_{}'.format(label)
                self.cache_handler.set(key, 'acme', TEN_MINUTES)
                with self.assertRaises(ValueError) as context:
                    self.cache_handler.set(key, 'widget', expire)
                self.assertEqual(message.format(expire), str(context.exception))
                self.assertEqual('acme', self.cache_handler.get(key))
                self.assertIn(self._server_ttl(key), (599, 600))

    def test_an_expire_the_cache_cannot_keep_exactly_never_creates_the_key(self):
        for label, (expire, _) in WRONG_EXPIRES.items():
            with self.subTest(label):
                key = 'widget_new_{}'.format(label)
                with self.assertRaises(ValueError):
                    self.cache_handler.set(key, 'acme', expire)
                self.assertIsNone(self.cache_handler.get(key))

    def test_an_expire_of_exactly_thirty_days_is_kept_in_full(self):
        self.cache_handler.set('widget_thirty_days', 'acme', timedelta(days=30))
        self.assertEqual('acme', self.cache_handler.get('widget_thirty_days'))
        self.assertIn(self._server_ttl('widget_thirty_days'), (THIRTY_DAYS_SECONDS - 1, THIRTY_DAYS_SECONDS))

    def test_an_expire_over_thirty_days_is_kept_in_full(self):
        for label, expire in LONG_EXPIRES.items():
            with self.subTest(label):
                key = 'widget_{}'.format(label)
                self.cache_handler.set(key, 'acme', expire)
                self.assertEqual('acme', self.cache_handler.get(key))
                expected = int(expire.total_seconds()) + self._server_clock_lag()
                ttl = self._server_ttl(key)
                self.assertGreaterEqual(ttl, expected - ABSOLUTE_EXPIRE_CLOCK_SLACK_SECONDS)
                self.assertLessEqual(ttl, expected + ABSOLUTE_EXPIRE_CLOCK_SLACK_SECONDS)

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

    def test_a_value_just_under_the_item_limit_round_trips_whole(self):
        large_str = 'a' * (ITEM_LIMIT_BYTES - 200)
        large_list = [{'position': i, 'name': 'widget'} for i in range(10_000)]
        self.cache_handler.set('widget_large_str', large_str, None)
        self.cache_handler.set('widget_large_list', large_list, None)
        self.assertEqual(large_str, self.cache_handler.get('widget_large_str'))
        self.assertEqual(large_list, self.cache_handler.get('widget_large_list'))

    def test_a_value_over_the_item_limit_raises_without_the_key_and_stores_nothing(self):
        too_large = 'a' * (ITEM_LIMIT_BYTES + 10)
        with self.assertRaises(RuntimeError) as context:
            self.cache_handler.set('widget_of_reviewer@acme.example', too_large, None)
        self.assertEqual(NOT_STORED_MESSAGE.format(ITEM_LIMIT_BYTES + 12), str(context.exception))  # + 2 JSON quotes
        self.assertNotIn('reviewer@acme.example', str(context.exception))
        self.assertIsNone(self.cache_handler.get('widget_of_reviewer@acme.example'))

    def test_a_value_over_the_item_limit_raises_and_keeps_the_stored_value(self):
        self.cache_handler.set('widget_replaced', 'acme', TEN_MINUTES)
        with self.assertRaises(RuntimeError):
            self.cache_handler.set('widget_replaced', 'a' * (ITEM_LIMIT_BYTES + 10), None)
        self.assertEqual('acme', self.cache_handler.get('widget_replaced'))
        self.assertIn(self._server_ttl('widget_replaced'), (599, 600))

    def test_set_refuses_every_unsupported_type_and_keeps_the_stored_value(self):
        for label, (value, type_text) in REFUSED_VALUES.items():
            with self.subTest(label):
                key = 'widget_{}'.format(label)
                self.cache_handler.set(key, 'acme', TEN_MINUTES)
                with self.assertRaises(ValueError) as context:
                    self.cache_handler.set(key, value, None)
                self.assertEqual(REFUSED_MESSAGE.format(type_text), str(context.exception))
                self.assertEqual('acme', self.cache_handler.get(key))
                self.assertIn(self._server_ttl(key), (599, 600))

    def test_set_refuses_an_unsupported_type_without_creating_the_key(self):
        with self.assertRaises(ValueError):
            self.cache_handler.set('widget_never_created', {'acme'}, None)
        self.assertIsNone(self._server_ttl('widget_never_created'))

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
        self.assertEqual(NO_EXPIRY_TTL, self._server_ttl('widget_replaced'))

    def test_set_replaces_the_value_and_adds_an_expiry(self):
        self.cache_handler.set('widget_replaced', 'acme', None)
        self.cache_handler.set('widget_replaced', ['widget'], TEN_MINUTES)
        self.assertEqual(['widget'], self.cache_handler.get('widget_replaced'))
        self.assertIn(self._server_ttl('widget_replaced'), (599, 600))

    def test_a_refused_key_raises_on_every_operation_and_is_never_rewritten(self):
        for label, (key, error_class) in REFUSED_KEYS.items():
            operations = {
                'set': lambda key=key: self.cache_handler.set(key, 'acme', None),
                'get': lambda key=key: self.cache_handler.get(key),
                'delete': lambda key=key: self.cache_handler.delete(key),
            }
            for operation_label, operation in operations.items():
                with self.subTest(key=label, operation=operation_label), self.assertRaises(error_class):
                    operation()
        self.assertIsNone(self.memcached_client.get('acme_widget'))  # no rewritten twin was stored

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
        self.assertIsNone(self._server_ttl('widget_deleted'))
        self.assertEqual('widget', self.cache_handler.get('widget_kept'))

    def test_delete_removes_a_key_that_has_an_expiry(self):
        self.cache_handler.set('widget_expiring', 'acme', TEN_MINUTES)
        self.cache_handler.delete('widget_expiring')
        self.assertIsNone(self._server_ttl('widget_expiring'))

    def test_delete_of_an_absent_key_does_nothing(self):
        self.cache_handler.set('widget_kept', 'widget', None)
        self.cache_handler.delete('widget_never_stored')
        self.assertEqual('widget', self.cache_handler.get('widget_kept'))

    def test_a_deleted_key_can_be_stored_again(self):
        self.cache_handler.set('widget_reused', 'acme', TEN_MINUTES)
        self.cache_handler.delete('widget_reused')
        self.cache_handler.set('widget_reused', 'widget', None)
        self.assertEqual('widget', self.cache_handler.get('widget_reused'))
        self.assertEqual(NO_EXPIRY_TTL, self._server_ttl('widget_reused'))

    def test_flush_all_empties_the_cache_and_the_handler_keeps_working(self):
        self.cache_handler.set('widget_forever', {'name': 'acme'}, None)
        self.cache_handler.set('widget_expiring', ['widget'], TEN_MINUTES)
        self.cache_handler.set('widget_monthly', 'reviewer', timedelta(days=31))
        self.cache_handler.flush_all()
        self.assertIsNone(self.cache_handler.get('widget_forever'))
        self.assertIsNone(self.cache_handler.get('widget_expiring'))
        self.assertIsNone(self.cache_handler.get('widget_monthly'))
        self.cache_handler.set('widget_after_flush', 'acme', None)
        self.assertEqual('acme', self.cache_handler.get('widget_after_flush'))

    def test_flush_all_of_an_empty_cache_does_nothing(self):
        self.cache_handler.flush_all()
        self.assertIsNone(self.cache_handler.get('widget_never_stored'))

    def test_two_handlers_on_one_url_share_their_values(self):
        second_cache_handler = CacheHandlerMemcached(MEMCACHED_URL)  # another process pointed at the same cache
        self.addCleanup(second_cache_handler.memcached_client.disconnect_all)
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
            self.cache_handler.memcached_client.disconnect_all()  # the client keeps one connection per thread
            return mismatches

        with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
            mismatches = [mismatch for found in executor.map(store_and_read, range(THREAD_COUNT)) for mismatch in found]
        self.assertEqual([], mismatches)
        for thread_number in range(THREAD_COUNT):
            expected = {'thread': thread_number, 'round': ROUNDS_PER_THREAD - 1}
            self.assertEqual(expected, self._stored('widget_thread_{}'.format(thread_number)))

    def test_an_unreachable_server_refuses_every_store_and_answers_reads_as_python_memcached_does(self):
        unreachable_cache_handler = self._unreachable_cache_handler()
        with self.assertRaises(RuntimeError) as context:
            unreachable_cache_handler.set('widget', 'acme', None)
        self.assertEqual(NOT_STORED_MESSAGE.format(len('"acme"')), str(context.exception))
        # python-memcached raises nothing for these: a read is a miss, a delete or flush does nothing
        self.assertIsNone(unreachable_cache_handler.get('widget'))
        self.assertIsNone(unreachable_cache_handler.delete('widget'))
        self.assertIsNone(unreachable_cache_handler.flush_all())
