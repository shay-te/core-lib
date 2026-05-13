"""Property-based tests for parse_utils.similarity."""
import unittest

from hypothesis import given, strategies as st

from core_lib.helpers.parse_utils import similarity
from tests.hypothesis_tests._settings import SETTINGS


class TestSimilarityProperties(unittest.TestCase):
    @given(st.text(min_size=1))
    @SETTINGS
    def test_self_similarity_is_one(self, s):
        self.assertEqual(similarity(s, s), 1.0)

    @given(st.text(), st.text())
    @SETTINGS
    def test_symmetric(self, a, b):
        self.assertEqual(similarity(a, b), similarity(b, a))

    @given(st.text(), st.text())
    @SETTINGS
    def test_in_unit_interval(self, a, b):
        s = similarity(a, b)
        self.assertGreaterEqual(s, 0.0)
        self.assertLessEqual(s, 1.0)
