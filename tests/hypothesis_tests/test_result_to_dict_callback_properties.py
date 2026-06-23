"""Property-based tests for the callback parameter of result_to_dict."""
import string as stringmod
import unittest

from hypothesis import given, strategies as st

from core_lib.data_transform.result_to_dict import result_to_dict
from tests.hypothesis_tests._settings import SETTINGS


_PRIMITIVE = st.one_of(
    st.integers(),
    st.text(),
    st.booleans(),
)
_STR_KEY = st.text(alphabet=stringmod.ascii_letters, min_size=1, max_size=10)


class TestResultToDictCallback(unittest.TestCase):
    @given(st.dictionaries(_STR_KEY, _PRIMITIVE, min_size=1, max_size=5))
    @SETTINGS
    def test_callback_receives_processed_dict(self, d):
        received = []
        def cb(results):
            received.append(results)
            return results
        result_to_dict(d, callback=cb)
        # Callback was invoked at least once with a dict
        self.assertTrue(any(isinstance(r, dict) for r in received))

    @given(st.dictionaries(_STR_KEY, _PRIMITIVE, min_size=1, max_size=5))
    @SETTINGS
    def test_callback_return_value_used(self, d):
        sentinel = object()
        def cb(results):
            return sentinel
        self.assertIs(result_to_dict(d, callback=cb), sentinel)

    @given(st.dictionaries(_STR_KEY, _PRIMITIVE, min_size=1, max_size=5))
    @SETTINGS
    def test_callback_returning_none_falls_back_to_results(self, d):
        # Per source: `results = callback(results) or results`
        def cb(results):
            return None
        result = result_to_dict(d, callback=cb)
        self.assertEqual(result, {str(k): v for k, v in d.items()})

    @given(st.dictionaries(_STR_KEY, _PRIMITIVE, min_size=1, max_size=5))
    @SETTINGS
    def test_callback_returning_empty_falls_back(self, d):
        # `{} or results` → results (since {} is falsy)
        def cb(results):
            return {}
        result = result_to_dict(d, callback=cb)
        self.assertEqual(result, {str(k): v for k, v in d.items()})

    @given(st.integers())
    @SETTINGS
    def test_callback_on_primitive_input(self, n):
        # Callback runs even on primitives — last in result_to_dict
        def cb(results):
            return ('wrapped', results)
        self.assertEqual(result_to_dict(n, callback=cb), ('wrapped', n))

    @given(st.dictionaries(_STR_KEY, _PRIMITIVE, min_size=1, max_size=5))
    @SETTINGS
    def test_no_callback_means_no_wrapping(self, d):
        # Without a callback the result is just the converted dict
        result = result_to_dict(d)
        self.assertEqual(result, {str(k): v for k, v in d.items()})
