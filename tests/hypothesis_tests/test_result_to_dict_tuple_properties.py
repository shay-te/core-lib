"""Property-based tests for result_to_dict on tuple inputs.

Regular tuples → tuple of converted values (same length).
NamedTuples (anything with non-empty _fields) → dict keyed by field name.
"""
import keyword
import string as stringmod
import unittest
from collections import namedtuple

from hypothesis import given, strategies as st

from core_lib.data_transform.result_to_dict import result_to_dict
from tests.hypothesis_tests._settings import SETTINGS


_PRIMITIVE = st.one_of(
    st.integers(),
    st.floats(allow_nan=False, allow_infinity=False),
    st.booleans(),
    st.text(),
)

# namedtuple field names cannot be Python keywords.
_FIELD_NAME = st.text(
    alphabet=stringmod.ascii_lowercase, min_size=2, max_size=8
).filter(lambda s: not keyword.iskeyword(s))


class TestResultToDictTuple(unittest.TestCase):
    @given(st.lists(_PRIMITIVE, max_size=10))
    @SETTINGS
    def test_regular_tuple_returns_tuple(self, items):
        result = result_to_dict(tuple(items))
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), len(items))

    @given(st.lists(_PRIMITIVE, min_size=1, max_size=10))
    @SETTINGS
    def test_regular_tuple_preserves_values(self, items):
        result = result_to_dict(tuple(items))
        self.assertEqual(result, tuple(items))

    def test_empty_tuple_returns_empty_tuple(self):
        # `isinstance(return_val, tuple)` is True for empty tuple.
        # No _fields → __tuple_to_dict([]) → empty tuple.
        self.assertEqual(result_to_dict(()), ())

    @given(
        st.lists(_FIELD_NAME, min_size=1, max_size=5, unique=True),
        st.lists(_PRIMITIVE, min_size=1, max_size=5),
    )
    @SETTINGS
    def test_namedtuple_returns_dict_with_field_names(self, field_names, values):
        # Match lengths
        n = min(len(field_names), len(values))
        if n == 0:
            return
        Cls = namedtuple('Cls', field_names[:n])
        instance = Cls(*values[:n])
        result = result_to_dict(instance)
        # Result is a dict keyed by field name with corresponding values
        self.assertIsInstance(result, dict)
        for fname, val in zip(field_names[:n], values[:n]):
            self.assertEqual(result[fname], val)

    @given(values=st.lists(_PRIMITIVE, min_size=1, max_size=5))
    @SETTINGS
    def test_namedtuple_dict_size_matches_fields(self, values):
        field_names = [f'f{i}' for i in range(len(values))]
        Cls = namedtuple('Cls', field_names)
        instance = Cls(*values)
        result = result_to_dict(instance)
        self.assertEqual(len(result), len(values))
