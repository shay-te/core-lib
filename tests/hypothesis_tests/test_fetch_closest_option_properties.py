"""Property-based tests for parse_utils.fetch_closest_option."""
import string as stringmod
import unittest

from hypothesis import given, strategies as st

from core_lib.helpers.parse_utils import fetch_closest_option
from tests.hypothesis_tests._settings import SETTINGS


_STRING_OPTION = st.text(
    alphabet=stringmod.ascii_lowercase, min_size=1, max_size=20
)


class TestFetchClosestOptionProperties(unittest.TestCase):
    @given(option=_STRING_OPTION, others=st.lists(_STRING_OPTION, max_size=5))
    @SETTINGS
    def test_exact_match_in_options_returns_one_of_them(self, option, others):
        options = [option] + others
        result = fetch_closest_option(option, options)
        # The result must be one of the options (and at threshold 0.89 the exact
        # match itself is the highest scoring).
        self.assertEqual(result, option)

    @given(
        source=_STRING_OPTION,
        options=st.lists(_STRING_OPTION, min_size=1, max_size=5),
    )
    @SETTINGS
    def test_result_is_from_options_or_none(self, source, options):
        result = fetch_closest_option(source, options)
        self.assertTrue(result is None or result in options)

    @given(source=st.one_of(st.integers(), st.floats(), st.lists(st.integers()), st.none()))
    @SETTINGS
    def test_non_string_source_returns_none(self, source):
        self.assertIsNone(fetch_closest_option(source, ['a', 'b']))

    @given(source=_STRING_OPTION)
    @SETTINGS
    def test_non_string_options_skipped(self, source):
        # All non-string options are silently skipped — with no valid matches,
        # nothing scores above the threshold so result is None.
        self.assertIsNone(fetch_closest_option(source, [True, False, 1, 2, None, []]))

    @given(
        source=_STRING_OPTION,
        threshold=st.floats(min_value=0.0, max_value=1.0),
    )
    @SETTINGS
    def test_self_in_options_with_low_threshold(self, source, threshold):
        # source is in options → similarity == 1.0 → always above threshold
        self.assertEqual(
            fetch_closest_option(source, [source], threshold=threshold), source
        )

    @given(source=_STRING_OPTION)
    @SETTINGS
    def test_threshold_1_0_only_accepts_perfect_match(self, source):
        self.assertEqual(
            fetch_closest_option(source, [source], threshold=1.0), source
        )

    @given(source=_STRING_OPTION, other=_STRING_OPTION)
    @SETTINGS
    def test_empty_options_returns_none(self, source, other):
        self.assertIsNone(fetch_closest_option(source, []))
