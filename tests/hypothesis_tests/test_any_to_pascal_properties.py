"""Property-based tests for string.any_to_pascal."""
import string as stringmod
import unittest

from hypothesis import assume, given, strategies as st

from core_lib.helpers.string import any_to_pascal
from tests.hypothesis_tests._settings import SETTINGS


# Avoid the leading-numeric edge case (which strips the first char)
_NO_LEADING_DIGIT = st.text(
    alphabet=stringmod.ascii_letters + ' _-', min_size=1, max_size=30
).filter(lambda s: len(s) > 0 and not s[0].isdigit())


class TestAnyToPascalProperties(unittest.TestCase):
    @given(_NO_LEADING_DIGIT)
    @SETTINGS
    def test_output_is_alphanumeric_only(self, s):
        out = any_to_pascal(s)
        # Result contains only letters and digits (no separators / whitespace)
        self.assertTrue(all(c.isalnum() for c in out))

    @given(_NO_LEADING_DIGIT)
    @SETTINGS
    def test_idempotent_on_alphabetic_pascal_input(self, s):
        # Restrict to alphabetic-only inputs to avoid the numeric-prefix
        # quirk that strips the leading char.
        assume(all(c.isalpha() or c in ' _-' for c in s))
        first = any_to_pascal(s)
        if first:
            assume(first[0].isalpha())
            second = any_to_pascal(first)
            self.assertEqual(first, second)

    @given(_NO_LEADING_DIGIT)
    @SETTINGS
    def test_no_separator_characters_in_output(self, s):
        out = any_to_pascal(s)
        for sep in ' _-':
            self.assertNotIn(sep, out)

    @given(
        words=st.lists(
            st.text(alphabet=stringmod.ascii_lowercase, min_size=1, max_size=10),
            min_size=1, max_size=5,
        )
    )
    @SETTINGS
    def test_lowercase_words_become_capitalized(self, words):
        snake = '_'.join(words)
        out = any_to_pascal(snake)
        # Output must start with uppercase
        self.assertTrue(out[0].isupper())
        # Output is purely letters
        self.assertTrue(out.isalpha())
        # Output length equals sum of word lengths
        self.assertEqual(len(out), sum(len(w) for w in words))
