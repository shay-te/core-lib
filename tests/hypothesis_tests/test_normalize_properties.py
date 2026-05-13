"""Property-based tests for parse_utils.normalize."""
import string as stringmod
import unittest

from hypothesis import given, strategies as st

from core_lib.helpers.parse_utils import normalize
from tests.hypothesis_tests._settings import SETTINGS


class TestNormalizeProperties(unittest.TestCase):
    @given(st.text())
    @SETTINGS
    def test_idempotent(self, s):
        once = normalize(s)
        twice = normalize(once)
        self.assertEqual(once, twice)

    @given(st.text())
    @SETTINGS
    def test_result_lowercase_only_letters_digits_spaces(self, s):
        out = normalize(s)
        allowed = set(stringmod.ascii_lowercase + stringmod.digits + ' ')
        self.assertTrue(all(c in allowed for c in out))

    @given(st.text())
    @SETTINGS
    def test_no_leading_or_trailing_whitespace(self, s):
        out = normalize(s)
        self.assertEqual(out, out.strip())

    @given(st.text())
    @SETTINGS
    def test_no_consecutive_spaces(self, s):
        out = normalize(s)
        self.assertNotIn('  ', out)

    @given(st.text(alphabet=stringmod.ascii_lowercase, min_size=1))
    @SETTINGS
    def test_already_normalized_passes_through(self, s):
        self.assertEqual(normalize(s), s)
