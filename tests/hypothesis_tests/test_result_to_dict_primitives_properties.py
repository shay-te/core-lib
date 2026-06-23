"""Property-based tests for result_to_dict on primitive inputs.

When none of the structured-type branches match (list/dict/tuple/Base/Row/
mongo Cursor), result_to_dict falls through to `else: results = return_val`,
returning the input unchanged. This includes int, float, bool, str, None,
and empty collections (which fail the `and return_val` truthiness guard).
"""
import unittest

from hypothesis import given, strategies as st

from core_lib.data_transform.result_to_dict import result_to_dict
from tests.hypothesis_tests._settings import SETTINGS


class TestResultToDictPrimitives(unittest.TestCase):
    @given(st.integers())
    @SETTINGS
    def test_integers_passthrough(self, n):
        self.assertEqual(result_to_dict(n), n)

    @given(st.floats(allow_nan=False, allow_infinity=False))
    @SETTINGS
    def test_floats_passthrough(self, f):
        self.assertEqual(result_to_dict(f), f)

    @given(st.booleans())
    @SETTINGS
    def test_booleans_passthrough(self, b):
        self.assertEqual(result_to_dict(b), b)

    @given(st.text())
    @SETTINGS
    def test_strings_passthrough(self, s):
        self.assertEqual(result_to_dict(s), s)

    def test_none_passthrough(self):
        self.assertIsNone(result_to_dict(None))

    def test_empty_list_passthrough(self):
        # `isinstance(return_val, list) and return_val` requires non-empty,
        # so empty list falls to else branch and is returned verbatim.
        self.assertEqual(result_to_dict([]), [])

    def test_empty_dict_passthrough(self):
        # Same as list: empty dict fails the truthiness guard.
        self.assertEqual(result_to_dict({}), {})

    @given(st.integers())
    @SETTINGS
    def test_primitive_ignores_properties_as_dict_flag(self, n):
        # The properties_as_dict recursion only fires if results is a dict
        self.assertEqual(result_to_dict(n, properties_as_dict=True), n)
        self.assertEqual(result_to_dict(n, properties_as_dict=False), n)

    @given(st.integers())
    @SETTINGS
    def test_primitive_with_callback_invokes_callback(self, n):
        captured = []
        def cb(results):
            captured.append(results)
            return results

        result = result_to_dict(n, callback=cb)
        self.assertEqual(result, n)
        self.assertEqual(captured, [n])
