"""Property-based tests for registry.default_registry.DefaultRegistry."""
import string as stringmod
import unittest

from hypothesis import given, strategies as st

from core_lib.registry.default_registry import DefaultRegistry
from tests.hypothesis_tests._settings import SETTINGS


class _Item:
    def __init__(self, n):
        self.n = n


class TestDefaultRegistryProperties(unittest.TestCase):
    @given(
        keys=st.lists(
            st.text(alphabet=stringmod.ascii_letters, min_size=1, max_size=10),
            min_size=1,
            max_size=10,
            unique=True,
        )
    )
    @SETTINGS
    def test_register_get_identity(self, keys):
        r = DefaultRegistry(_Item)
        items = {k: _Item(k) for k in keys}
        for k, v in items.items():
            r.register(k, v)
        for k, v in items.items():
            self.assertIs(r.get(k), v)

    @given(
        keys=st.lists(
            st.text(alphabet=stringmod.ascii_letters, min_size=1, max_size=10),
            min_size=1,
            max_size=10,
            unique=True,
        )
    )
    @SETTINGS
    def test_registered_returns_all_keys(self, keys):
        r = DefaultRegistry(_Item)
        for k in keys:
            r.register(k, _Item(k))
        self.assertEqual(set(r.registered()), set(keys))

    @given(
        keys=st.lists(
            st.text(alphabet=stringmod.ascii_letters, min_size=1, max_size=10),
            min_size=1,
            max_size=10,
            unique=True,
        )
    )
    @SETTINGS
    def test_unregister_all_yields_empty_registry(self, keys):
        r = DefaultRegistry(_Item)
        for k in keys:
            r.register(k, _Item(k))
        for k in keys:
            r.unregister(k)
        self.assertEqual(r.registered(), [])

    @given(
        keys=st.lists(
            st.text(alphabet=stringmod.ascii_letters, min_size=1, max_size=10),
            min_size=2,
            max_size=10,
            unique=True,
        )
    )
    @SETTINGS
    def test_default_get_returns_first_registered_when_no_default(self, keys):
        r = DefaultRegistry(_Item)
        items = [_Item(k) for k in keys]
        for k, item in zip(keys, items):
            r.register(k, item)
        # With no is_default, get() falls back to first registered
        self.assertIs(r.get(), items[0])
