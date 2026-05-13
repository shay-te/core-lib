"""Property-based round-trip tests for snake_to_camel / camel_to_snake."""
import string as stringmod
import unittest

from hypothesis import given, strategies as st

from core_lib.helpers.string import camel_to_snake, snake_to_camel
from tests.hypothesis_tests._settings import SETTINGS


class TestStringRoundTripProperties(unittest.TestCase):
    @given(
        st.lists(
            st.text(alphabet=stringmod.ascii_lowercase, min_size=1, max_size=10),
            min_size=1,
            max_size=5,
        )
    )
    @SETTINGS
    def test_snake_camel_snake_roundtrip(self, tokens):
        snake = '_'.join(tokens)
        camel = snake_to_camel(snake)
        back = camel_to_snake(camel)
        self.assertEqual(back, snake)

    @given(
        st.lists(
            st.text(alphabet=stringmod.ascii_lowercase, min_size=1, max_size=10),
            min_size=1,
            max_size=5,
        )
    )
    @SETTINGS
    def test_snake_to_camel_no_underscores_in_output(self, tokens):
        snake = '_'.join(tokens)
        camel = snake_to_camel(snake)
        self.assertNotIn('_', camel)

    @given(
        st.lists(
            st.text(alphabet=stringmod.ascii_lowercase, min_size=1, max_size=10),
            min_size=1,
            max_size=5,
        )
    )
    @SETTINGS
    def test_snake_to_camel_first_char_uppercase(self, tokens):
        snake = '_'.join(tokens)
        camel = snake_to_camel(snake)
        self.assertTrue(camel[0].isupper() or not camel[0].isalpha())
