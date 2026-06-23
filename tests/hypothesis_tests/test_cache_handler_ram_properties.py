"""Property-based tests for cache.cache_handler_ram.CacheHandlerRam."""
import unittest

from hypothesis import given, strategies as st

from core_lib.cache.cache_handler_ram import CacheHandlerRam
from tests.hypothesis_tests._settings import SETTINGS


class TestCacheHandlerRamProperties(unittest.TestCase):
    @given(
        key=st.text(min_size=1, max_size=50),
        value=st.one_of(
            st.text(min_size=1),
            st.integers(),
            st.lists(st.integers(), min_size=1),
            st.dictionaries(st.text(min_size=1), st.integers(), min_size=1),
        ),
    )
    @SETTINGS
    def test_set_then_get_is_identity(self, key, value):
        h = CacheHandlerRam()
        h.set(key, value, None)
        self.assertEqual(h.get(key), value)

    @given(
        keys=st.lists(
            st.text(min_size=1, max_size=20), min_size=1, max_size=10, unique=True
        )
    )
    @SETTINGS
    def test_flush_all_clears_everything(self, keys):
        h = CacheHandlerRam()
        for k in keys:
            h.set(k, 'v', None)
        h.flush_all()
        for k in keys:
            self.assertIsNone(h.get(k))

    @given(
        key=st.text(min_size=1, max_size=20),
        value=st.text(min_size=1, max_size=20),
    )
    @SETTINGS
    def test_delete_makes_get_return_none(self, key, value):
        h = CacheHandlerRam()
        h.set(key, value, None)
        h.delete(key)
        self.assertIsNone(h.get(key))

    @given(
        key=st.text(min_size=1, max_size=20),
        v1=st.integers(min_value=1),
        v2=st.integers(min_value=1),
    )
    @SETTINGS
    def test_set_overwrites_previous_value(self, key, v1, v2):
        """
        Verify that setting a key multiple times overwrites the previous value with the most recent one.
        """
        h = CacheHandlerRam()
        h.set(key, v1, None)
        h.set(key, v2, None)
        self.assertEqual(h.get(key), v2)
