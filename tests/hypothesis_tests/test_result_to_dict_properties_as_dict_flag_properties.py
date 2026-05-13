"""Property-based tests for the properties_as_dict parameter of result_to_dict.

Source:
    if isinstance(results, dict):
        if properties_as_dict:
            for key, value in results.items():
                if not isinstance(value, (int, float, bool, str)):
                    results[key] = result_to_dict(value, ...)

So properties_as_dict=True triggers recursion only on non-primitive dict
values. =False leaves them as-is.
"""
import string as stringmod
import unittest

from hypothesis import given, strategies as st

from core_lib.data_transform.result_to_dict import result_to_dict
from tests.hypothesis_tests._settings import SETTINGS


_PRIMITIVE = st.one_of(
    st.integers(),
    st.text(),
    st.booleans(),
    st.floats(allow_nan=False, allow_infinity=False),
)
_STR_KEY = st.text(alphabet=stringmod.ascii_letters, min_size=1, max_size=8)


class TestResultToDictPropertiesAsDictFlag(unittest.TestCase):
    @given(st.dictionaries(_STR_KEY, _PRIMITIVE, min_size=1, max_size=5))
    @SETTINGS
    def test_flag_irrelevant_for_primitive_values(self, d):
        # No non-primitive values means no recursion regardless of flag
        true_result = result_to_dict(d, properties_as_dict=True)
        false_result = result_to_dict(d, properties_as_dict=False)
        self.assertEqual(true_result, false_result)

    @given(
        outer_key=_STR_KEY,
        inner=st.dictionaries(_STR_KEY, _PRIMITIVE, min_size=1, max_size=3),
    )
    @SETTINGS
    def test_true_recurses_into_nested_dict(self, outer_key, inner):
        result = result_to_dict({outer_key: inner}, properties_as_dict=True)
        # Inner dict was processed too — keys still coerced
        for k, v in inner.items():
            self.assertEqual(result[outer_key][str(k)], v)

    @given(
        outer_key=_STR_KEY,
        inner=st.dictionaries(_STR_KEY, _PRIMITIVE, min_size=1, max_size=3),
    )
    @SETTINGS
    def test_false_keeps_nested_dict_object(self, outer_key, inner):
        result = result_to_dict({outer_key: inner}, properties_as_dict=False)
        # Nested dict is the same object — no recursion
        self.assertIs(result[outer_key], inner)

    @given(
        outer_key=_STR_KEY,
        inner_list=st.lists(_PRIMITIVE, min_size=1, max_size=3),
    )
    @SETTINGS
    def test_true_recurses_into_nested_list(self, outer_key, inner_list):
        # Lists are not primitive → recursion fires.
        result = result_to_dict({outer_key: inner_list}, properties_as_dict=True)
        self.assertEqual(result[outer_key], inner_list)

    @given(
        outer_key=_STR_KEY,
        inner_list=st.lists(_PRIMITIVE, min_size=1, max_size=3),
    )
    @SETTINGS
    def test_false_keeps_nested_list_object(self, outer_key, inner_list):
        result = result_to_dict({outer_key: inner_list}, properties_as_dict=False)
        self.assertIs(result[outer_key], inner_list)
