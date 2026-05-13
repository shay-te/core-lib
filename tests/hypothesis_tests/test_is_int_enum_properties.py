"""Property-based tests for validation.is_int_enum."""
import enum
import unittest

from hypothesis import given, strategies as st

from core_lib.helpers.validation import is_int_enum
from tests.hypothesis_tests._settings import SETTINGS


class _Color(enum.Enum):
    RED = 1
    GREEN = 2
    BLUE = 3
    YELLOW = 4
    PURPLE = 5


_VALID_VALUES = [m.value for m in _Color]


class TestIsIntEnumProperties(unittest.TestCase):
    @given(st.sampled_from(_VALID_VALUES))
    @SETTINGS
    def test_valid_enum_values_accepted(self, value):
        self.assertTrue(is_int_enum(value, _Color))

    @given(st.integers().filter(lambda n: n not in _VALID_VALUES))
    @SETTINGS
    def test_invalid_values_rejected(self, n):
        self.assertFalse(is_int_enum(n, _Color))

    @given(st.sampled_from(_VALID_VALUES))
    @SETTINGS
    def test_none_enum_class_returns_false(self, value):
        self.assertFalse(is_int_enum(value, None))

    @given(st.sampled_from(_VALID_VALUES))
    @SETTINGS
    def test_non_enum_class_returns_false(self, value):
        # Calling a random class with the value can throw; the suppress()
        # context catches it and returns False.
        self.assertFalse(is_int_enum(value, 'not_an_enum'))
        self.assertFalse(is_int_enum(value, 42))

    def test_none_value_rejected(self):
        self.assertFalse(is_int_enum(None, _Color))
