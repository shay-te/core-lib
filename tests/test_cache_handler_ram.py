"""`CacheHandlerRam` keeps any key and any value as given (no JSON, so a hit returns the stored object itself) with
an expire of any length. Like Redis and memcached, it refuses an expire of 0 or less."""
import sys
import threading
import unittest
from datetime import datetime, timedelta
from time import sleep

from core_lib.cache.cache_handler_ram import CacheHandlerRam

TEN_MINUTES = timedelta(minutes=10)
STORED_OBJECTS = {
    'dict': {'name': 'acme', 'tags': ['widget', 'reviewer'], 'count': 2},
    'dict_with_int_keys': {1: 'acme', 2: 'widget'},
    'list': ['acme', 1, {'nested': True}, None],
    'int': 42,
    'float': 1.5,
    'tuple': ('acme', 1),
    'set': {'acme', 'widget'},
    'bytes': b'acme',
    'datetime': datetime(2026, 1, 2, 3, 4, 5),
    'object': object(),
    'str': 'acme widget',
    'zero': 0,
    'empty_str': '',
    'empty_list': [],
    'empty_dict': {},
}
KEYS_OTHER_CACHES_REFUSE = {
    'empty': '',
    'space': 'acme widget',
    'tab': 'acme\twidget',
    'newline': 'acme\nwidget',
    'delete_127': 'acme\x7fwidget',
    'ascii_5000_bytes': 'k' * 5000,
    'non_ascii_over_250_bytes': '✓' * 84,
}
NOT_POSITIVE_EXPIRES = {
    'zero': timedelta(0),  # without the check, a zero expire kept the value forever (`if data['expire']` is falsy)
    'minus_one_microsecond': timedelta(microseconds=-1),
    'minus_five_seconds': timedelta(seconds=-5),
}
THREAD_COUNT = 16
KEYS_PER_ROUND = 50


class TestCacheHandlerRam(unittest.TestCase):

    def setUp(self):
        self.cache_handler = CacheHandlerRam()

    def test_every_object_reads_back_as_the_same_object(self):
        for label, value in STORED_OBJECTS.items():
            with self.subTest(label):
                self.cache_handler.set('widget_{}'.format(label), value, None)
                self.assertIs(value, self.cache_handler.get('widget_{}'.format(label)))

    def test_every_key_memcached_refuses_is_kept_and_matched_exactly(self):
        for label, key in KEYS_OTHER_CACHES_REFUSE.items():
            with self.subTest(label):
                self.cache_handler.set(key, label, None)
        for label, key in KEYS_OTHER_CACHES_REFUSE.items():
            with self.subTest(label):
                self.assertEqual(label, self.cache_handler.get(key))
                self.cache_handler.delete(key)
                self.assertIsNone(self.cache_handler.get(key))
        self.assertIsNone(self.cache_handler.get('acme_widget'))  # 'acme widget' was never stored as 'acme_widget'

    def test_get_of_an_absent_key_returns_none(self):
        self.assertIsNone(self.cache_handler.get('widget_never_stored'))

    def test_a_one_second_expire_neither_ends_early_nor_late(self):
        self.cache_handler.set('widget_short', 'acme', timedelta(seconds=1))
        sleep(0.5)
        self.assertEqual('acme', self.cache_handler.get('widget_short'))
        sleep(0.6)
        self.assertIsNone(self.cache_handler.get('widget_short'))

    def test_a_part_of_a_second_is_kept_exactly(self):
        self.cache_handler.set('widget_blink', 'acme', timedelta(milliseconds=600))
        self.cache_handler.set('widget_second', 'acme', timedelta(seconds=1, milliseconds=300))
        sleep(0.4)
        self.assertEqual(['acme', 'acme'], [self.cache_handler.get('widget_blink'),
                                            self.cache_handler.get('widget_second')])
        sleep(0.4)
        self.assertEqual([None, 'acme'], [self.cache_handler.get('widget_blink'),
                                          self.cache_handler.get('widget_second')])
        sleep(0.6)
        self.assertIsNone(self.cache_handler.get('widget_second'))

    def test_a_set_with_no_expire_drops_the_old_expiry(self):
        self.cache_handler.set('widget_replaced', 'old', timedelta(seconds=1))
        self.cache_handler.set('widget_replaced', 'new', None)
        sleep(1.1)
        self.assertEqual('new', self.cache_handler.get('widget_replaced'))

    def test_a_set_with_a_longer_expire_replaces_the_shorter_one(self):
        self.cache_handler.set('widget_replaced', 'old', timedelta(seconds=1))
        self.cache_handler.set('widget_replaced', 'new', TEN_MINUTES)
        sleep(1.1)
        self.assertEqual('new', self.cache_handler.get('widget_replaced'))

    def test_an_expire_of_zero_or_less_raises_and_keeps_the_stored_value(self):
        for label, expire in NOT_POSITIVE_EXPIRES.items():
            with self.subTest(label):
                self.cache_handler.set('widget', 'acme', TEN_MINUTES)
                with self.assertRaises(ValueError) as context:
                    self.cache_handler.set('widget', 'widget', expire)
                self.assertEqual('expire must be more than 0. got `{!r}`'.format(expire), str(context.exception))
                self.assertEqual('acme', self.cache_handler.get('widget'))

    def test_a_one_microsecond_expire_is_kept_as_given(self):
        self.cache_handler.set('widget_blink', 'acme', timedelta(microseconds=1))
        sleep(0.01)
        self.assertIsNone(self.cache_handler.get('widget_blink'))

    def test_delete_removes_only_that_key(self):
        self.cache_handler.set('widget_deleted', 'acme', None)
        self.cache_handler.set('widget_kept', 'widget', None)
        self.cache_handler.delete('widget_deleted')
        self.cache_handler.delete('widget_never_stored')
        self.assertIsNone(self.cache_handler.get('widget_deleted'))
        self.assertEqual('widget', self.cache_handler.get('widget_kept'))

    def test_flush_all_empties_the_cache_and_the_handler_keeps_working(self):
        self.cache_handler.set('widget_forever', 'acme', None)
        self.cache_handler.flush_all()
        self.assertIsNone(self.cache_handler.get('widget_forever'))
        self.cache_handler.set('widget_after_flush', 'acme', None)
        self.assertEqual('acme', self.cache_handler.get('widget_after_flush'))

    def test_concurrent_reads_and_deletes_of_expired_keys_never_raise(self):
        previous_interval = sys.getswitchinterval()
        sys.setswitchinterval(1e-6)  # switch threads as often as possible, to hit the race if there is one
        self.addCleanup(sys.setswitchinterval, previous_interval)
        long_ago = datetime.utcnow() - timedelta(minutes=1)
        errors = []

        def read_and_delete(barrier: threading.Barrier):
            barrier.wait()
            for key_number in range(KEYS_PER_ROUND):
                try:
                    self.cache_handler.get('widget_{}'.format(key_number))
                    self.cache_handler.delete('widget_{}'.format(key_number))
                except Exception as error:
                    errors.append(error)

        for _ in range(50):
            for key_number in range(KEYS_PER_ROUND):
                self.cache_handler.set('widget_{}'.format(key_number), 'acme', timedelta(seconds=1))
                self.cache_handler.cached_function_responses['widget_{}'.format(key_number)]['set_time'] = long_ago
            barrier = threading.Barrier(THREAD_COUNT)
            threads = [threading.Thread(target=read_and_delete, args=(barrier,)) for _ in range(THREAD_COUNT)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
        self.assertEqual([], errors)
