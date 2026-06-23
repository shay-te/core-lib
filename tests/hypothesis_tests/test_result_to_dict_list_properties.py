"""Property-based tests for result_to_dict on list inputs."""
import string as stringmod
import unittest

from hypothesis import given, strategies as st

from core_lib.data_transform.result_to_dict import result_to_dict
from tests.hypothesis_tests._settings import SETTINGS


_PRIMITIVE = st.one_of(
    st.integers(),
    st.floats(allow_nan=False, allow_infinity=False),
    st.booleans(),
    st.text(),
)


class TestResultToDictList(unittest.TestCase):
    @given(st.lists(_PRIMITIVE, min_size=1, max_size=20))
    @SETTINGS
    def test_list_of_primitives_preserves_values(self, items):
        self.assertEqual(result_to_dict(items), items)

    @given(st.lists(_PRIMITIVE, min_size=1, max_size=20))
    @SETTINGS
    def test_list_length_preserved(self, items):
        self.assertEqual(len(result_to_dict(items)), len(items))

    @given(st.lists(_PRIMITIVE, min_size=1, max_size=20))
    @SETTINGS
    def test_list_order_preserved(self, items):
        result = result_to_dict(items)
        self.assertEqual(result, items)

    @given(
        st.lists(
            st.dictionaries(
                st.text(alphabet=stringmod.ascii_letters, min_size=1, max_size=10),
                _PRIMITIVE,
                min_size=1,
                max_size=5,
            ),
            min_size=1,
            max_size=10,
        )
    )
    @SETTINGS
    def test_list_of_dicts_each_recursed(self, dicts):
        result = result_to_dict(dicts)
        self.assertEqual(len(result), len(dicts))
        for d, r in zip(dicts, result):
            for k, v in d.items():
                self.assertEqual(r[str(k)], v)

    @given(st.lists(_PRIMITIVE, min_size=1, max_size=10))
    @SETTINGS
    def test_callback_invoked_per_element(self, items):
        captured = []
        def cb(r):
            captured.append(r)
            return r
        result_to_dict(items, callback=cb)
        # Callback called once per element (top-level list returns early
        # without applying callback to the list itself).
        self.assertEqual(len(captured), len(items))

    @given(st.lists(st.lists(_PRIMITIVE, min_size=1, max_size=3), min_size=1, max_size=5))
    @SETTINGS
    def test_nested_lists_recursed(self, nested):
        result = result_to_dict(nested)
        self.assertEqual(result, nested)
