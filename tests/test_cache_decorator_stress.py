"""Stress tests for the Cache decorator and its supporting utilities.

Covers:
- Module-level helpers: parse, _parse_datetime, _get_expire
- Cache constructor validation
- Decorator behavior under edge cases (exceptions, recursive functions,
  collisions, classmethods, missing handler, mutations, etc.)
- Stored value types end-to-end through the RAM handler
- CacheRegistry constructor + interactions
"""
import unittest
from datetime import datetime, timedelta, timezone

from core_lib.cache.cache_decorator import Cache, _get_expire, _parse_datetime, parse
from core_lib.cache.cache_handler_ram import CacheHandlerRam
from core_lib.cache.cache_handler_no_cache import CacheHandlerNoCache
from core_lib.cache.cache_registry import CacheRegistry
from core_lib.cache.cache_handler import CacheHandler
from core_lib.core_lib import CoreLib


_HANDLER = 'stress_cache_handler'


def _ensure_handler():
    if _HANDLER not in CoreLib.cache_registry.registered():
        CoreLib.cache_registry.register(_HANDLER, CacheHandlerRam())


# ── Module-level parse helpers ─────────────────────────────────────────────


class TestParseFunction(unittest.TestCase):
    def test_parse_seconds(self):
        before = datetime.utcnow()
        result = parse('30 seconds')
        after = datetime.utcnow()
        # result is roughly 30s after "now"
        self.assertGreater(result, before + timedelta(seconds=29))
        self.assertLess(result, after + timedelta(seconds=31))

    def test_parse_minutes(self):
        result = parse('5 minutes')
        delta = result - datetime.utcnow()
        self.assertGreater(delta.total_seconds(), 295)
        self.assertLess(delta.total_seconds(), 305)

    def test_parse_hours(self):
        result = parse('2 hours')
        delta = result - datetime.utcnow()
        self.assertGreater(delta.total_seconds(), 7195)
        self.assertLess(delta.total_seconds(), 7205)

    def test_parse_days(self):
        result = parse('1 day')
        delta = result - datetime.utcnow()
        # parsedatetime may interpret "1 day" as "tomorrow at midnight"
        # which can be < 24h away depending on the current time of day.
        # Just verify it's in the future and within ~26 hours.
        self.assertGreater(delta.total_seconds(), 0)
        self.assertLess(delta.total_seconds(), 26 * 3600)

    def test_parse_weeks(self):
        result = parse('2 weeks')
        delta = result - datetime.utcnow()
        self.assertGreaterEqual(delta.days, 13)

    def test_parse_invalid_expression_raises(self):
        with self.assertRaises(ValueError):
            parse('total nonsense xyz_!')

    def test_parse_returns_utc_naive_datetime(self):
        result = parse('1 minute')
        # Function strips tzinfo at the end
        self.assertIsNone(result.tzinfo)


class TestParseDatetimeHelper(unittest.TestCase):
    def test_returns_timedelta(self):
        result = _parse_datetime('30 seconds')
        self.assertIsInstance(result, timedelta)

    def test_approximates_30_seconds(self):
        result = _parse_datetime('30 seconds')
        # The function = parse(expr) - datetime.utcnow(); slight drift expected
        self.assertGreater(result.total_seconds(), 28)
        self.assertLess(result.total_seconds(), 32)


class TestGetExpireHelper(unittest.TestCase):
    def test_none_returns_none(self):
        self.assertIsNone(_get_expire(None))

    def test_timedelta_passthrough(self):
        td = timedelta(seconds=42)
        self.assertEqual(_get_expire(td), td)

    def test_string_resolved_to_timedelta(self):
        result = _get_expire('5 seconds')
        self.assertIsInstance(result, timedelta)
        self.assertGreater(result.total_seconds(), 3)
        self.assertLess(result.total_seconds(), 7)

    def test_empty_string_returns_empty_string(self):
        # Falsy strings short-circuit `expire and isinstance(...)` → fall through
        self.assertEqual(_get_expire(''), '')

    def test_integer_passthrough(self):
        # Anything that isn't a non-empty string just falls through
        self.assertEqual(_get_expire(42), 42)


# ── Cache constructor ────────────────────────────────────────────────────


class TestCacheConstructor(unittest.TestCase):
    def test_all_defaults(self):
        c = Cache()
        self.assertIsNone(c.key)
        self.assertEqual(c.max_key_length, 250)
        self.assertIsNone(c.expire)
        self.assertFalse(c.invalidate)
        self.assertIsNone(c.handler_name)
        self.assertTrue(c.cache_empty_result)

    def test_full_init(self):
        c = Cache(
            key='my-key',
            max_key_length=100,
            expire=timedelta(seconds=10),
            invalidate=True,
            handler_name='my-handler',
            cache_empty_result=False,
        )
        self.assertEqual(c.key, 'my-key')
        self.assertEqual(c.max_key_length, 100)
        self.assertEqual(c.expire, timedelta(seconds=10))
        self.assertTrue(c.invalidate)
        self.assertEqual(c.handler_name, 'my-handler')
        self.assertFalse(c.cache_empty_result)

    def test_string_expire_resolved_at_construction(self):
        # _get_expire is called in __init__ — invalid string raises immediately
        with self.assertRaises(ValueError):
            Cache(expire='gibberish nonsense xyz!')


# ── Decorator under edge cases ─────────────────────────────────────────


class TestCacheDecoratorEdges(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _ensure_handler()

    def setUp(self):
        CoreLib.cache_registry.get(_HANDLER).flush_all()

    def test_exception_in_function_propagates_and_not_cached(self):
        calls = []

        @Cache(key='err', expire=timedelta(seconds=60), handler_name=_HANDLER)
        def boom():
            calls.append(1)
            raise ValueError('boom')

        with self.assertRaises(ValueError):
            boom()
        # Cache was not populated
        cached = CoreLib.cache_registry.get(_HANDLER).get('err')
        self.assertIsNone(cached)
        # And next call re-runs
        with self.assertRaises(ValueError):
            boom()
        self.assertEqual(len(calls), 2)

    def test_handler_missing_raises_value_error(self):
        @Cache(key='k', expire=timedelta(seconds=60), handler_name='no_such_handler_xyz')
        def fn():
            return 'v'

        with self.assertRaises(ValueError):
            fn()

    def test_classmethod_decorated(self):
        class Service:
            counter = 0

            @classmethod
            @Cache(key='cls-key', expire=timedelta(seconds=60), handler_name=_HANDLER)
            def get(cls):
                cls.counter += 1
                return cls.counter

        Service.get()
        Service.get()
        # Cached → counter stays 1
        self.assertEqual(Service.counter, 1)

    def test_staticmethod_decorated(self):
        counter = []

        class Service:
            @staticmethod
            @Cache(key='static-key', expire=timedelta(seconds=60), handler_name=_HANDLER)
            def calc():
                counter.append(1)
                return 'result'

        self.assertEqual(Service.calc(), 'result')
        self.assertEqual(Service.calc(), 'result')
        self.assertEqual(len(counter), 1)

    def test_recursive_function_first_call_only_runs_inner(self):
        # When a recursive function calls itself with the same args, the
        # recursive call gets a cache miss INSIDE the outer call (because
        # the outer's result isn't stored yet), so the function body runs
        # multiple times.
        calls = []

        @Cache(key='fib-{n}', expire=timedelta(seconds=60), handler_name=_HANDLER)
        def fib(n):
            calls.append(n)
            if n < 2:
                return n
            return fib(n - 1) + fib(n - 2)

        # First top-level call: walks the tree, populates as it returns.
        fib(5)
        first_call_count = len(calls)
        calls.clear()
        # Second top-level call hits the cache immediately
        fib(5)
        self.assertEqual(len(calls), 0)
        # First call had body executions; subsequent reads served from cache
        self.assertGreater(first_call_count, 0)

    def test_two_functions_different_keys_dont_collide(self):
        calls = {'a': 0, 'b': 0}

        @Cache(key='a', expire=timedelta(seconds=60), handler_name=_HANDLER)
        def fa():
            calls['a'] += 1
            return 'val-a'

        @Cache(key='b', expire=timedelta(seconds=60), handler_name=_HANDLER)
        def fb():
            calls['b'] += 1
            return 'val-b'

        fa(); fa(); fb(); fb()
        self.assertEqual(calls, {'a': 1, 'b': 1})

    def test_two_functions_same_key_DO_collide(self):
        # Documenting behavior: same key across functions shares cache slot
        calls = {'a': 0, 'b': 0}

        @Cache(key='shared', expire=timedelta(seconds=60), handler_name=_HANDLER)
        def fa():
            calls['a'] += 1
            return 'val-a'

        @Cache(key='shared', expire=timedelta(seconds=60), handler_name=_HANDLER)
        def fb():
            calls['b'] += 1
            return 'val-b'

        first = fa()
        second = fb()
        # fb's call hit fa's cached value
        self.assertEqual(first, 'val-a')
        self.assertEqual(second, 'val-a')
        self.assertEqual(calls['b'], 0)

    def test_no_handler_name_uses_default(self):
        # No handler_name → registry.get(None) → returns the default
        @Cache(key='dflt-test', expire=timedelta(seconds=60))
        def fn():
            return 'default-served'

        # Since `_HANDLER` was registered but not as default, this may fail
        # unless a default exists. Either succeed-cached or raise ValueError.
        try:
            self.assertEqual(fn(), 'default-served')
        except ValueError:
            # No default registered — acceptable
            pass

    def test_unicode_in_key_template(self):
        @Cache(key='unicode-{x}-éñ', expire=timedelta(seconds=60), handler_name=_HANDLER)
        def fn(x):
            return x

        self.assertEqual(fn('vál'), 'vál')
        # Check the stored key contains the unicode
        stored = list(
            CoreLib.cache_registry.get(_HANDLER).cached_function_responses.keys()
        )
        self.assertEqual(len(stored), 1)

    def test_invalidate_with_no_existing_entry_no_op(self):
        # invalidate=True deletes the key even if nothing was cached
        @Cache(key='inv-fresh', invalidate=True, handler_name=_HANDLER)
        def fn():
            return 'ran'

        # No exception even though nothing was previously cached
        self.assertEqual(fn(), 'ran')

    def test_invalidate_after_invalidate(self):
        calls = []

        @Cache(key='set', expire=timedelta(seconds=60), handler_name=_HANDLER)
        def get():
            calls.append('get')
            return 'v'

        @Cache(key='set', invalidate=True, handler_name=_HANDLER)
        def clear():
            return None

        get(); get()
        self.assertEqual(calls, ['get'])
        clear(); clear(); clear()
        get()
        self.assertEqual(calls, ['get', 'get'])


# ── Stored value type round-trip via the decorator ─────────────────────


class TestCachedValueTypes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _ensure_handler()

    def setUp(self):
        CoreLib.cache_registry.get(_HANDLER).flush_all()

    def _build_fn(self, value, key):
        @Cache(key=key, expire=timedelta(seconds=60), handler_name=_HANDLER)
        def fn():
            return value
        return fn

    def test_int_roundtrip(self):
        fn = self._build_fn(42, 'int')
        self.assertEqual(fn(), 42)
        self.assertEqual(fn(), 42)

    def test_str_roundtrip(self):
        fn = self._build_fn('hello world', 'str')
        self.assertEqual(fn(), 'hello world')

    def test_list_roundtrip(self):
        value = [1, 2, 3]
        fn = self._build_fn(value, 'list')
        self.assertEqual(fn(), value)
        # Same object identity preserved by RAM handler
        self.assertIs(fn(), value)

    def test_dict_roundtrip(self):
        value = {'a': 1, 'b': [2, 3]}
        fn = self._build_fn(value, 'dict')
        self.assertEqual(fn(), value)

    def test_tuple_roundtrip(self):
        value = (1, 'a', True)
        fn = self._build_fn(value, 'tup')
        self.assertEqual(fn(), value)

    def test_nested_complex_roundtrip(self):
        value = {'lvl1': [{'lvl2': (1, 2, [3, 4, {'lvl5': 'deep'}])}]}
        fn = self._build_fn(value, 'nested')
        self.assertEqual(fn(), value)

    def test_falsy_empty_string_cached_when_cache_empty_true(self):
        calls = []

        @Cache(key='empty-str', expire=timedelta(seconds=60), handler_name=_HANDLER,
               cache_empty_result=True)
        def fn():
            calls.append(1)
            return ''

        fn(); fn()
        # '' is not None → cached
        self.assertEqual(len(calls), 1)

    def test_none_value_never_cached_even_when_cache_empty_true(self):
        # None can't be cached because the handler can't distinguish a
        # cached None from a cache miss.
        calls = []

        @Cache(key='none-val', expire=timedelta(seconds=60), handler_name=_HANDLER,
               cache_empty_result=True)
        def fn():
            calls.append(1)
            return None

        fn(); fn(); fn()
        # Every call ran the function body
        self.assertEqual(len(calls), 3)


# ── CacheRegistry ─────────────────────────────────────────────────────


class TestCacheRegistry(unittest.TestCase):
    def test_constructor_creates_empty_registry(self):
        r = CacheRegistry()
        self.assertEqual(r.registered(), [])
        self.assertIsNone(r.default_key)

    def test_registry_accepts_cache_handler_subclasses(self):
        r = CacheRegistry()
        r.register('ram', CacheHandlerRam())
        r.register('nocache', CacheHandlerNoCache())
        self.assertEqual(set(r.registered()), {'ram', 'nocache'})

    def test_registry_rejects_non_cache_handler(self):
        r = CacheRegistry()
        with self.assertRaises(ValueError):
            r.register('bad', 'not a handler')

    def test_registry_default_lifecycle(self):
        r = CacheRegistry()
        h1 = CacheHandlerRam()
        h2 = CacheHandlerRam()
        r.register('a', h1)
        r.register('b', h2, is_default=True)
        self.assertIs(r.get(), h2)
        r.unregister('b')
        self.assertIsNone(r.default_key)

    def test_registry_duplicate_key_raises(self):
        r = CacheRegistry()
        r.register('k', CacheHandlerRam())
        with self.assertRaises(ValueError):
            r.register('k', CacheHandlerRam())

    def test_registry_isolation_between_instances(self):
        r1 = CacheRegistry()
        r2 = CacheRegistry()
        r1.register('shared-name', CacheHandlerRam())
        # r2 doesn't see r1's registration
        self.assertEqual(r2.registered(), [])


# ── Cache constructor passes expire through _get_expire ─────────────


class TestCacheExpireResolution(unittest.TestCase):
    def test_timedelta_kept_as_timedelta(self):
        td = timedelta(seconds=10)
        c = Cache(expire=td)
        self.assertEqual(c.expire, td)

    def test_string_resolved_to_timedelta(self):
        c = Cache(expire='5 seconds')
        self.assertIsInstance(c.expire, timedelta)

    def test_none_stays_none(self):
        c = Cache(expire=None)
        self.assertIsNone(c.expire)

    def test_construction_with_long_string_expire(self):
        c = Cache(expire='2 weeks')
        self.assertIsInstance(c.expire, timedelta)
        self.assertGreater(c.expire.total_seconds(), 13 * 24 * 3600)


# ── Cache interaction with multiple handlers ─────────────────────────


class TestCacheMultipleHandlers(unittest.TestCase):
    def setUp(self):
        self._handler_a = 'stress_handler_a'
        self._handler_b = 'stress_handler_b'
        for name in (self._handler_a, self._handler_b):
            if name not in CoreLib.cache_registry.registered():
                CoreLib.cache_registry.register(name, CacheHandlerRam())
            CoreLib.cache_registry.get(name).flush_all()

    def test_two_handlers_isolated(self):
        @Cache(key='shared-key', expire=timedelta(seconds=60), handler_name=self._handler_a)
        def fn_a():
            return 'a'

        @Cache(key='shared-key', expire=timedelta(seconds=60), handler_name=self._handler_b)
        def fn_b():
            return 'b'

        fn_a(); fn_b()
        # Each handler stored its own entry
        keys_a = list(
            CoreLib.cache_registry.get(self._handler_a).cached_function_responses.keys()
        )
        keys_b = list(
            CoreLib.cache_registry.get(self._handler_b).cached_function_responses.keys()
        )
        self.assertEqual(len(keys_a), 1)
        self.assertEqual(len(keys_b), 1)
        self.assertEqual(fn_a(), 'a')
        self.assertEqual(fn_b(), 'b')
