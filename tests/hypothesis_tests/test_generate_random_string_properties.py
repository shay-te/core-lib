"""Property-based tests for helpers.generate_data.generate_random_string."""
import string as stringmod
import unittest

from hypothesis import given, strategies as st

from core_lib.helpers.generate_data import generate_random_string
from tests.hypothesis_tests._settings import SETTINGS


class TestGenerateRandomStringProperties(unittest.TestCase):
    @given(length=st.integers(min_value=0, max_value=200))
    @SETTINGS
    def test_length_respected(self, length):
        self.assertEqual(len(generate_random_string(length=length)), length)

    @given(length=st.integers(min_value=1, max_value=50))
    @SETTINGS
    def test_no_flags_returns_only_lowercase(self, length):
        s = generate_random_string(length=length)
        self.assertTrue(all(c in stringmod.ascii_lowercase for c in s))

    @given(length=st.integers(min_value=1, max_value=50))
    @SETTINGS
    def test_upper_only_uses_letters(self, length):
        s = generate_random_string(length=length, upper=True)
        self.assertTrue(all(c in stringmod.ascii_letters for c in s))

    @given(length=st.integers(min_value=1, max_value=50))
    @SETTINGS
    def test_full_charset_uses_only_printable(self, length):
        s = generate_random_string(length=length, upper=True, digits=True, special=True)
        allowed = (
            stringmod.ascii_letters + stringmod.digits + stringmod.punctuation
        )
        self.assertTrue(all(c in allowed for c in s))

    @given(length=st.integers(min_value=1, max_value=50))
    @SETTINGS
    def test_digits_only_extends_lowercase(self, length):
        s = generate_random_string(length=length, digits=True)
        allowed = stringmod.ascii_lowercase + stringmod.digits
        self.assertTrue(all(c in allowed for c in s))
