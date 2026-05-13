"""Property-based tests for validation.is_bool."""
import string as stringmod
import unittest

from hypothesis import given, strategies as st

from core_lib.helpers.validation import is_bool
from tests.hypothesis_tests._settings import SETTINGS


class TestIsBoolProperties(unittest.TestCase):
    @given(st.booleans())
    @SETTINGS
    def test_python_bools_accepted(self, b):
        self.assertTrue(is_bool(b))

    @given(st.sampled_from(['true', 'True', 'TRUE', 'TrUe', 'false', 'False', 'FALSE']))
    @SETTINGS
    def test_case_insensitive_true_false_strings_accepted(self, s):
        self.assertTrue(is_bool(s))

    @given(
        st.text(alphabet=stringmod.ascii_letters, min_size=1, max_size=10).filter(
            lambda s: s.lower() not in ('true', 'false')
        )
    )
    @SETTINGS
    def test_arbitrary_strings_rejected(self, s):
        self.assertFalse(is_bool(s))

    @given(st.integers().filter(lambda n: not isinstance(n, bool)))
    @SETTINGS
    def test_integers_rejected(self, n):
        # Python ints are not bools (bool is a subclass but value 0/1 as int isn't bool)
        # is_bool checks isinstance(val, bool) which is True for True/False but False for
        # any plain int
        self.assertFalse(is_bool(n))

    @given(st.floats(allow_nan=False, allow_infinity=False))
    @SETTINGS
    def test_floats_rejected(self, f):
        self.assertFalse(is_bool(f))

    @given(st.one_of(st.lists(st.integers()), st.dictionaries(st.text(), st.integers()),
                     st.sets(st.integers()), st.tuples(st.integers())))
    @SETTINGS
    def test_collections_rejected(self, c):
        self.assertFalse(is_bool(c))

    def test_none_rejected(self):
        self.assertFalse(is_bool(None))
