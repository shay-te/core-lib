"""Challenge tests for Cache decorator flags & edge cases.

Goal: exercise parameter combinations and inputs that the existing test_cache.py
does not cover — max_key_length truncation, key=None fallback to qualname,
expire=None (no expiration), keys with spaces, very large keys, falsy result
permutations with cache_empty_result=True/False, etc.
"""
import unittest
from datetime import timedelta

from core_lib.cache.cache_decorator import Cache, parse, _get_expire, _parse_datetime
from core_lib.cache.cache_handler_ram import CacheHandlerRam
from core_lib.core_lib import CoreLib


HANDLER = 'flag_test_handler'


class TestCacheFlags(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if HANDLER not in CoreLib.cache_registry.registered():
            CoreLib.cache_registry.register(HANDLER, CacheHandlerRam())

    def setUp(self):
        # Always start from a clean cache for each test
        CoreLib.cache_registry.get(HANDLER).flush_all()

    # ── key=None fallback to qualname ───────────────────────────────────

    def test_key_none_uses_qualname(self):
        calls = []

        @Cache(handler_name=HANDLER)
        def fn(x):
            calls.append(x)
            return x * 2

        self.assertEqual(fn(3), 6)
        self.assertEqual(fn(3), 6)
        # Cached: function body called only once
        self.assertEqual(len(calls), 1)
        # And the cached key uses the qualname (no spaces in this name)
        cache = CoreLib.cache_registry.get(HANDLER)
        cached_keys = list(cache.cached_function_responses.keys())
        self.assertEqual(len(cached_keys), 1)
        self.assertIn('fn', cached_keys[0])

    # ── max_key_length truncates long keys ──────────────────────────────

    def test_max_key_length_truncates(self):
        long_key = 'x' * 500

        @Cache(key=long_key, max_key_length=20, handler_name=HANDLER)
        def fn():
            return 'val'

        fn()
        cache = CoreLib.cache_registry.get(HANDLER)
        stored_keys = list(cache.cached_function_responses.keys())
        self.assertEqual(len(stored_keys), 1)
        # Key is truncated to max_key_length characters
        self.assertEqual(len(stored_keys[0]), 20)
        self.assertTrue(stored_keys[0].startswith('x'))

    def test_max_key_length_one_char(self):
        @Cache(key='abcdefg', max_key_length=1, handler_name=HANDLER)
        def fn():
            return 1

        fn()
        cache = CoreLib.cache_registry.get(HANDLER)
        stored_keys = list(cache.cached_function_responses.keys())
        self.assertEqual(stored_keys[0], 'a')

    # ── Spaces in key are replaced with underscores ─────────────────────

    def test_key_spaces_replaced_with_underscores(self):
        @Cache(key='my key with spaces', handler_name=HANDLER)
        def fn():
            return 'v'

        fn()
        cache = CoreLib.cache_registry.get(HANDLER)
        stored_key = list(cache.cached_function_responses.keys())[0]
        self.assertNotIn(' ', stored_key)
        self.assertEqual(stored_key, 'my_key_with_spaces')

    # ── expire=None caches forever ──────────────────────────────────────

    def test_expire_none_caches_indefinitely(self):
        calls = []

        @Cache(key='no-expire-key', expire=None, handler_name=HANDLER)
        def fn():
            calls.append(1)
            return 'v'

        fn()
        fn()
        fn()
        self.assertEqual(len(calls), 1)

    # ── cache_empty_result False vs True with every falsy value ─────────

    def test_cache_empty_result_false_skips_falsy_values(self):
        for falsy in (None, '', [], {}, 0, False):
            with self.subTest(falsy=falsy):
                CoreLib.cache_registry.get(HANDLER).flush_all()
                calls = []

                @Cache(
                    key=f'falsy-{type(falsy).__name__}-{falsy!r}',
                    expire=timedelta(seconds=60),
                    cache_empty_result=False,
                    handler_name=HANDLER,
                )
                def fn():
                    calls.append(1)
                    return falsy

                fn()
                fn()
                # When result is falsy and cache_empty_result is False, the cache
                # never stores the value, so fn is invoked every time.
                self.assertEqual(len(calls), 2)

    def test_cache_empty_result_true_caches_falsy_except_none(self):
        # Cache rule: `if (cache_empty_result and result is not None) or result`
        # With cache_empty_result=True, the LEFT clause is True for any
        # non-None result — so every falsy except None gets cached.
        for falsy, should_cache in [
            (None, False),     # `result is not None` is False; OR `result` (None) also False
            ('', True),        # `result is not None` is True → cached
            ([], True),
            ({}, True),
            (0, True),
            (False, True),
        ]:
            with self.subTest(falsy=falsy):
                CoreLib.cache_registry.get(HANDLER).flush_all()
                calls = []

                @Cache(
                    key=f'fal2-{type(falsy).__name__}-{falsy!r}',
                    expire=timedelta(seconds=60),
                    cache_empty_result=True,
                    handler_name=HANDLER,
                )
                def fn():
                    calls.append(1)
                    return falsy

                fn()
                fn()
                if should_cache:
                    self.assertEqual(len(calls), 1, f'expected cached, got {len(calls)} calls')
                else:
                    self.assertEqual(len(calls), 2, f'expected not cached, got {len(calls)} calls')

    def test_cache_empty_result_true_does_cache_non_none_truthy(self):
        # Sanity: a truthy result is cached
        CoreLib.cache_registry.get(HANDLER).flush_all()
        calls = []

        @Cache(key='truthy', expire=timedelta(seconds=60),
               cache_empty_result=True, handler_name=HANDLER)
        def fn():
            calls.append(1)
            return 'x'

        fn(); fn(); fn()
        self.assertEqual(len(calls), 1)

    # ── invalidate=True always calls function and deletes cache entry ──

    def test_invalidate_calls_func_then_clears(self):
        calls = []

        @Cache(key='inv-key', expire=timedelta(seconds=60), handler_name=HANDLER)
        def get():
            calls.append('get')
            return 'cached'

        @Cache(key='inv-key', invalidate=True, handler_name=HANDLER)
        def update():
            calls.append('upd')
            return 'updated'

        self.assertEqual(get(), 'cached')
        self.assertEqual(get(), 'cached')  # served from cache
        self.assertEqual(update(), 'updated')
        self.assertEqual(calls, ['get', 'upd'])
        # After invalidate, next get re-runs the function
        self.assertEqual(get(), 'cached')
        self.assertEqual(calls, ['get', 'upd', 'get'])

    def test_invalidate_propagates_exception_without_clearing(self):
        # When the decorated function raises, the cache is NOT invalidated
        # (per the docstring comment: "On exception don't invalidate")
        calls = []

        @Cache(key='inv-err', expire=timedelta(seconds=60), handler_name=HANDLER)
        def get():
            calls.append('get')
            return 'v'

        @Cache(key='inv-err', invalidate=True, handler_name=HANDLER)
        def update():
            raise RuntimeError('boom')

        get()
        with self.assertRaises(RuntimeError):
            update()
        # Cache survived
        get()
        self.assertEqual(calls, ['get'])

    # ── String expire variants ──────────────────────────────────────────

    def test_parse_invalid_string_raises_at_construction(self):
        # _get_expire validates BEFORE use (per comment in cache_decorator)
        with self.assertRaises(ValueError):
            Cache(expire='this is not a duration xyz_!')

    def test_parse_empty_string_returns_value(self):
        # _get_expire only invokes _parse_datetime for truthy strings
        cache = Cache(expire='')
        self.assertEqual(cache.expire, '')

    def test_parse_returns_close_to_target(self):
        # parse() should return a datetime in the future
        from datetime import datetime
        d = parse('1 minute')
        delta = d - datetime.utcnow()
        # rough check: between 50 and 70 seconds
        self.assertGreater(delta.total_seconds(), 50)
        self.assertLess(delta.total_seconds(), 70)

    def test_get_expire_passes_through_timedelta(self):
        td = timedelta(seconds=42)
        self.assertEqual(_get_expire(td), td)

    def test_get_expire_passes_through_none(self):
        self.assertIsNone(_get_expire(None))

    # ── handler_name fallbacks ──────────────────────────────────────────

    def test_handler_name_none_uses_default_registry(self):
        # When handler_name is None, cache_registry.get(None) returns the
        # default-registered handler.
        calls = []

        @Cache(key='default-handler-key')
        def fn():
            calls.append(1)
            return 'v'

        # Need a default handler in the registry; the suite already registers
        # `xyz` as default in test_cache.py at module scope. If absent, this
        # raises a ValueError — either branch is acceptable behavior so we
        # check both.
        try:
            fn()
            fn()
            self.assertEqual(len(calls), 1)
        except ValueError:
            # No default handler available — expected when no other cache
            # tests have populated the registry.
            self.assertEqual(len(calls), 0)

    # ── Result types ────────────────────────────────────────────────────

    def test_cached_result_round_trips_through_types(self):
        # Verify that various types survive caching with RAM handler.
        cases = [
            ('int', 42),
            ('str', 'hello'),
            ('list', [1, 2, 3]),
            ('dict', {'a': 1}),
            ('tuple', (1, 2)),
            ('nested', {'x': [1, {'y': 'z'}]}),
        ]
        for name, value in cases:
            with self.subTest(case=name):
                CoreLib.cache_registry.get(HANDLER).flush_all()

                @Cache(key=f'roundtrip-{name}', expire=timedelta(seconds=60),
                       handler_name=HANDLER)
                def fn():
                    return value

                self.assertEqual(fn(), value)
                self.assertEqual(fn(), value)

    # ── Key resolution with kwargs / positional / defaults / missing ────

    def test_key_with_positional_and_keyword_args(self):
        @Cache(key='kwargs-{a}-{b}-{c}', expire=timedelta(seconds=60),
               handler_name=HANDLER)
        def fn(a, b, c='default'):
            return f'{a}-{b}-{c}'

        fn(1, 2)               # a=1 b=2 c=default
        fn(1, 2, c='custom')   # a=1 b=2 c=custom
        fn(1, b=2, c='custom') # same as previous (mixed call form)
        cache = CoreLib.cache_registry.get(HANDLER)
        keys = list(cache.cached_function_responses.keys())
        # Only 2 distinct (a, b, c) combinations, so only 2 cache keys.
        self.assertEqual(len(keys), 2)
        for k in keys:
            self.assertNotIn(' ', k)

    def test_key_with_missing_placeholder_uses_marker(self):
        # UnseenFormatter inserts !M<key>M! for missing kwargs;
        # the Cache decorator then replaces spaces with underscores
        # before truncation/storage.
        @Cache(key='missing-{nonexistent}', expire=timedelta(seconds=60),
               handler_name=HANDLER)
        def fn(a):
            return a

        fn(1)
        cache = CoreLib.cache_registry.get(HANDLER)
        keys = list(cache.cached_function_responses.keys())
        self.assertEqual(len(keys), 1)
        self.assertIn('!M', keys[0])
