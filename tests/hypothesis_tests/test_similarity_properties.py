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

    # NOTE: similarity (difflib.SequenceMatcher.ratio) is NOT symmetric in
    # general — `SequenceMatcher('tide', 'diet').ratio() == 0.25` while
    # `SequenceMatcher('diet', 'tide').ratio() == 0.5`. The non-symmetry is
    # documented Python behavior; we don't claim it. Surfaced by hypothesis.

    @given(st.text(), st.text())
    @SETTINGS
    def test_in_unit_interval(self, a, b):
        s = similarity(a, b)
        self.assertGreaterEqual(s, 0.0)
        self.assertLessEqual(s, 1.0)
