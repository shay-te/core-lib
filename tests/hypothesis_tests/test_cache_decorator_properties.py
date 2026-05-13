"""Property-based tests for cache.cache_decorator.Cache.

Invariant: decorating a deterministic function with Cache must produce a
function whose results are stable across repeated calls with the same args,
and whose stored key respects max_key_length and contains no spaces.
"""
import string as stringmod
import unittest
from datetime import timedelta

from hypothesis import given, strategies as st

from core_lib.cache.cache_decorator import Cache
from core_lib.cache.cache_handler_ram import CacheHandlerRam
from core_lib.core_lib import CoreLib
from tests.hypothesis_tests._settings import SETTINGS


_HANDLER = 'hyp_cache_handler'


class TestCacheDecoratorProperties(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if _HANDLER not in CoreLib.cache_registry.registered():
            CoreLib.cache_registry.register(_HANDLER, CacheHandlerRam())

    def setUp(self):
        CoreLib.cache_registry.get(_HANDLER).flush_all()

    @given(
        key=st.text(
            alphabet=stringmod.ascii_letters + ' ',
            min_size=1,
            max_size=50,
        )
    )
    @SETTINGS
    def test_stored_key_never_contains_spaces(self, key):
        CoreLib.cache_registry.get(_HANDLER).flush_all()

        @Cache(key=key, expire=timedelta(seconds=60), handler_name=_HANDLER)
        def fn():
            return 'v'

        fn()
        stored_keys = list(
            CoreLib.cache_registry.get(_HANDLER).cached_function_responses.keys()
        )
        self.assertEqual(len(stored_keys), 1)
        self.assertNotIn(' ', stored_keys[0])

    @given(
        max_len=st.integers(min_value=1, max_value=30),
        key=st.text(
            alphabet=stringmod.ascii_letters,
            min_size=50,
            max_size=200,
        ),
    )
    @SETTINGS
    def test_stored_key_truncated_to_max_key_length(self, max_len, key):
        CoreLib.cache_registry.get(_HANDLER).flush_all()

        @Cache(
            key=key,
            max_key_length=max_len,
            expire=timedelta(seconds=60),
            handler_name=_HANDLER,
        )
        def fn():
            return 'v'

        fn()
        stored_keys = list(
            CoreLib.cache_registry.get(_HANDLER).cached_function_responses.keys()
        )
        self.assertEqual(len(stored_keys), 1)
        self.assertLessEqual(len(stored_keys[0]), max_len)

    @given(value=st.integers(min_value=1))
    @SETTINGS
    def test_repeated_call_returns_cached(self, value):
        CoreLib.cache_registry.get(_HANDLER).flush_all()
        counter = {'n': 0}

        @Cache(
            key=f'value-{value}',
            expire=timedelta(seconds=60),
            handler_name=_HANDLER,
        )
        def fn():
            counter['n'] += 1
            return value

        first = fn()
        second = fn()
        self.assertEqual(first, second)
        self.assertEqual(counter['n'], 1)  # body called only once

    @given(
        seed=st.integers(min_value=1, max_value=10000),
        value=st.one_of(
            st.text(
                alphabet=stringmod.ascii_letters + stringmod.digits,
                min_size=1,
                max_size=20,
            ),
            st.integers(min_value=1),
            st.lists(st.integers(), min_size=1, max_size=5),
        ),
    )
    @SETTINGS
    def test_cached_value_equals_function_output(self, seed, value):
        # Use a clean digits-only key so format-string placeholders inside
        # `value` don't leak into the key template parsed by UnseenFormatter.
        CoreLib.cache_registry.get(_HANDLER).flush_all()

        @Cache(
            key=f'k-{seed}',
            expire=timedelta(seconds=60),
            handler_name=_HANDLER,
        )
        def fn():
            return value

        self.assertEqual(fn(), value)
