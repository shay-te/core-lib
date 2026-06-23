"""Property-based tests for result_to_dict on dict inputs."""
import string as stringmod
import unittest

from hypothesis import given, strategies as st

from core_lib.data_transform.result_to_dict import result_to_dict
from tests.hypothesis_tests._settings import SETTINGS


_PRIMITIVE_VALUE = st.one_of(
    st.integers(),
    st.floats(allow_nan=False, allow_infinity=False),
    st.booleans(),
    st.text(),
)

_STR_KEY = st.text(alphabet=stringmod.ascii_letters, min_size=1, max_size=10)


class TestResultToDictDict(unittest.TestCase):
    @given(st.dictionaries(_STR_KEY, _PRIMITIVE_VALUE, min_size=1, max_size=10))
    @SETTINGS
    def test_dict_of_primitives_preserves_values(self, d):
        result = result_to_dict(d)
        for k, v in d.items():
            # Keys are coerced to string by __dict_to_dict
            self.assertEqual(result[str(k)], v)

    @given(st.dictionaries(_STR_KEY, _PRIMITIVE_VALUE, min_size=1, max_size=10))
    @SETTINGS
    def test_dict_keys_always_strings(self, d):
        result = result_to_dict(d)
        for k in result:
            self.assertIsInstance(k, str)

    @given(st.dictionaries(st.integers(), _PRIMITIVE_VALUE, min_size=1, max_size=5))
    @SETTINGS
    def test_int_keys_coerced_to_string(self, d):
        result = result_to_dict(d)
        for orig_key, v in d.items():
            self.assertEqual(result[str(orig_key)], v)

    @given(st.dictionaries(_STR_KEY, _PRIMITIVE_VALUE, min_size=1, max_size=10))
    @SETTINGS
    def test_length_preserved(self, d):
        result = result_to_dict(d)
        # str(k) collisions are unlikely with letter-only keys
        self.assertEqual(len(result), len(d))

    @given(st.dictionaries(_STR_KEY, _PRIMITIVE_VALUE, min_size=1, max_size=10))
    @SETTINGS
    def test_idempotent_on_primitive_dict(self, d):
        once = result_to_dict(d)
        twice = result_to_dict(once)
        self.assertEqual(once, twice)

    @given(
        outer_key=_STR_KEY,
        inner=st.dictionaries(_STR_KEY, _PRIMITIVE_VALUE, min_size=1, max_size=5),
    )
    @SETTINGS
    def test_nested_dict_recursed_when_properties_as_dict_true(self, outer_key, inner):
        nested = {outer_key: inner}
        result = result_to_dict(nested, properties_as_dict=True)
        # Inner dict was recursed → keys still match (coerced to strings)
        for k, v in inner.items():
            self.assertEqual(result[outer_key][str(k)], v)

    @given(
        outer_key=_STR_KEY,
        inner=st.dictionaries(_STR_KEY, _PRIMITIVE_VALUE, min_size=1, max_size=5),
    )
    @SETTINGS
    def test_nested_dict_not_recursed_when_properties_as_dict_false(self, outer_key, inner):
        nested = {outer_key: inner}
        result = result_to_dict(nested, properties_as_dict=False)
        # Inner dict is the same object, no recursion
        self.assertIs(result[outer_key], inner)
