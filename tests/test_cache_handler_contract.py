"""What every cache handler does the same: a stored JSON value reads back equal, absent / replaced / deleted /
flushed keys read alike, a value expires on time, and an expire of 0 or less raises and keeps the stored value. Each
case runs on the RAM, Redis and memcached handlers side by side, and what each returned or raised (type and message)
must be equal. The no-cache handler stores nothing and checks nothing: its own test shows it keeps nothing.

What a backend adds stays its own and is tested in its own file: RAM keeps any key, any object and any expire;
Redis any key and an expire to the millisecond; memcached refuses keys itself and keeps whole seconds; Redis and
memcached keep JSON.

RAM always takes part. Redis and memcached join when `CORE_LIB_TEST_REDIS_URL` /
`CORE_LIB_TEST_MEMCACHED_URL` name THROWAWAY servers (every case empties them); without them,
`test_redis_and_memcached_take_part` is skipped, so a run that compared only RAM shows `skipped=`."""
import os
import unittest
from datetime import timedelta
from time import sleep

from core_lib.cache.cache_handler_memcached import CacheHandlerMemcached
from core_lib.cache.cache_handler_no_cache import CacheHandlerNoCache
from core_lib.cache.cache_handler_ram import CacheHandlerRam
from core_lib.cache.cache_handler_redis import CacheHandlerRedis

REDIS_URL = os.environ.get('CORE_LIB_TEST_REDIS_URL')
MEMCACHED_URL = os.environ.get('CORE_LIB_TEST_MEMCACHED_URL')
TEN_MINUTES = timedelta(minutes=10)
SHORT_EXPIRE = timedelta(seconds=3)  # memcached's clock ticks once a second: such an item lives 2 to 3 seconds
STORED_VALUES = {  # values JSON keeps exactly, so every handler returns them equal
    'dict': {'zeta': 1, 'alpha': [None, True, 'acme']},
    'list': ['acme', 1, 0.5, {'nested': False}],
    'int': -7,
    'int_past_64_bits': 2 ** 100,
    'true': True,
    'str': 'acme \u2713 \U0001F600',
    'str_null': 'null',
    'zero': 0,
    'empty_str': '',
    'empty_list': [],
    'empty_dict': {},
}

NOT_POSITIVE_EXPIRES = (timedelta(0), timedelta(microseconds=-1), timedelta(seconds=-5), timedelta(days=-31))


def _outcome(call) -> tuple:
    try:
        return 'returned', call()
    except Exception as error:
        return 'raised', type(error).__name__, str(error)


class TestCacheHandlerContract(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.storing_handlers = {'ram': CacheHandlerRam()}
        if REDIS_URL:
            cls.storing_handlers['redis'] = CacheHandlerRedis(REDIS_URL)
        if MEMCACHED_URL:
            cls.storing_handlers['memcached'] = CacheHandlerMemcached(MEMCACHED_URL)

    @classmethod
    def tearDownClass(cls):
        for cache_handler in cls.storing_handlers.values():
            cache_handler.flush_all()

    def _assert_same_outcome(self, handlers: dict, case):
        for cache_handler in handlers.values():
            cache_handler.flush_all()
        outcomes = {name: _outcome(lambda: case(cache_handler)) for name, cache_handler in handlers.items()}
        first = next(iter(outcomes.values()))
        self.assertEqual({name: first for name in outcomes}, outcomes)
        return first

    def test_redis_and_memcached_take_part(self):
        if not (REDIS_URL and MEMCACHED_URL):
            self.skipTest('set CORE_LIB_TEST_REDIS_URL and CORE_LIB_TEST_MEMCACHED_URL to compare every handler')
        self.assertEqual({'ram', 'redis', 'memcached'}, set(self.storing_handlers))

    def test_every_stored_json_value_reads_back_equal_on_every_handler(self):
        for label, value in STORED_VALUES.items():
            with self.subTest(label):
                def case(cache_handler, value=value):
                    cache_handler.set('widget', value, TEN_MINUTES)
                    read_back = cache_handler.get('widget')
                    return type(read_back).__name__, read_back
                outcome = self._assert_same_outcome(self.storing_handlers, case)
                self.assertEqual(('returned', (type(value).__name__, value)), outcome)

    def test_absent_replaced_deleted_and_flushed_keys_read_the_same_on_every_handler(self):
        cases = {
            'absent': lambda cache_handler: cache_handler.get('widget'),
            'replaced': lambda cache_handler: [cache_handler.set('widget', 'old', TEN_MINUTES),
                                               cache_handler.set('widget', ['new'], None), cache_handler.get('widget')],
            'deleted': lambda cache_handler: [cache_handler.set('widget', 'acme', None),
                                              cache_handler.delete('widget'), cache_handler.get('widget')],
            'absent_deleted': lambda cache_handler: cache_handler.delete('widget'),
            'flushed': lambda cache_handler: [cache_handler.set('widget', 'acme', None),
                                              cache_handler.flush_all(), cache_handler.get('widget')],
        }
        for label, case in cases.items():
            with self.subTest(label):
                self._assert_same_outcome(self.storing_handlers, case)

    def test_an_expire_of_zero_or_less_raises_the_same_and_keeps_the_stored_value_on_every_handler(self):
        for expire in NOT_POSITIVE_EXPIRES:
            with self.subTest(repr(expire)):
                def case(cache_handler, expire=expire):
                    cache_handler.set('widget', 'acme', None)
                    outcome = _outcome(lambda: cache_handler.set('widget', 'widget', expire))
                    return [outcome, cache_handler.get('widget')]
                outcome = self._assert_same_outcome(self.storing_handlers, case)
                expected_error = ('raised', 'ValueError', 'expire must be more than 0. got `{!r}`'.format(expire))
                self.assertEqual(('returned', [expected_error, 'acme']), outcome)

    def test_a_value_expires_the_same_on_every_handler(self):
        for cache_handler in self.storing_handlers.values():
            cache_handler.flush_all()
            cache_handler.set('widget_expiring', 'acme', SHORT_EXPIRE)
            cache_handler.set('widget_forever', 'acme', None)
        before = {name: cache_handler.get('widget_expiring') for name, cache_handler in self.storing_handlers.items()}
        sleep(3.2)
        after = {name: [cache_handler.get('widget_expiring'), cache_handler.get('widget_forever')]
                 for name, cache_handler in self.storing_handlers.items()}
        self.assertEqual({name: 'acme' for name in self.storing_handlers}, before)
        self.assertEqual({name: [None, 'acme'] for name in self.storing_handlers}, after)

    def test_the_no_cache_handler_keeps_nothing_it_accepts(self):
        no_cache = CacheHandlerNoCache()
        no_cache.set('widget', {'name': 'acme'}, TEN_MINUTES)
        no_cache.set('widget_forever', 'acme', None)
        no_cache.delete('widget_never_stored')
        no_cache.flush_all()
        self.assertEqual([None, None], [no_cache.get('widget'), no_cache.get('widget_forever')])
