"""Property-based tests for parse_utils.clean_list."""
import unittest

from hypothesis import given, strategies as st

from core_lib.helpers.parse_utils import clean_list
from tests.hypothesis_tests._settings import SETTINGS


class TestCleanListProperties(unittest.TestCase):
    @given(st.lists(st.integers(min_value=1, max_value=1000)))
    @SETTINGS
    def test_no_filter_on_positive_ints(self, items):
        self.assertEqual(clean_list(items), items)

    @given(
        st.lists(
            st.one_of(
                st.just(None), st.just(''), st.just([]), st.just({}), st.just(())
            )
        )
    )
    @SETTINGS
    def test_all_filterable_yields_empty(self, items):
        self.assertEqual(clean_list(items), [])

    @given(st.lists(st.integers(min_value=1)))
    @SETTINGS
    def test_preserves_order(self, items):
        result = clean_list(items)
        self.assertEqual(result, items)
