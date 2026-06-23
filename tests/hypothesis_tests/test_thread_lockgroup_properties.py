"""Property-based tests for helpers.thread.LockGroup."""
import string as stringmod
import unittest
from datetime import timedelta

from hypothesis import given, strategies as st

from core_lib.helpers.thread import LockGroup
from tests.hypothesis_tests._settings import SETTINGS


_KEY_STRATEGY = st.text(alphabet=stringmod.ascii_letters, min_size=1, max_size=10)


class TestLockGroupProperties(unittest.TestCase):
    @given(_KEY_STRATEGY)
    @SETTINGS
    def test_same_key_returns_same_lock(self, key):
        group = LockGroup(timedelta(seconds=60))
        a = group.get_lock(key)
        b = group.get_lock(key)
        self.assertIs(a, b)

    @given(
        keys=st.lists(_KEY_STRATEGY, min_size=2, max_size=10, unique=True),
    )
    @SETTINGS
    def test_different_keys_return_different_locks(self, keys):
        group = LockGroup(timedelta(seconds=60))
        locks = [group.get_lock(k) for k in keys]
        # All distinct objects
        self.assertEqual(len({id(l) for l in locks}), len(keys))

    @given(_KEY_STRATEGY)
    @SETTINGS
    def test_clear_keeps_recent_keys(self, key):
        # max_age large → clear() doesn't drop the recently-touched key
        group = LockGroup(timedelta(hours=1))
        group.get_lock(key)
        group.clear()
        # Still present
        self.assertIn(key, group.lock_dict)
