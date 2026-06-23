"""Property-based tests for the ResultToDict decorator class."""
import string as stringmod
import unittest

from hypothesis import given, strategies as st

from core_lib.data_transform.result_to_dict import ResultToDict
from tests.hypothesis_tests._settings import SETTINGS


_PRIMITIVE = st.one_of(
    st.integers(),
    st.text(),
    st.booleans(),
)
_STR_KEY = st.text(alphabet=stringmod.ascii_letters, min_size=1, max_size=10)


class TestResultToDictDecorator(unittest.TestCase):
    @given(st.dictionaries(_STR_KEY, _PRIMITIVE, min_size=1, max_size=5))
    @SETTINGS
    def test_decorator_converts_function_return(self, d):
        @ResultToDict()
        def fn():
            return d

        result = fn()
        self.assertEqual(result, {str(k): v for k, v in d.items()})

    @given(st.integers())
    @SETTINGS
    def test_decorator_passes_primitive_through(self, n):
        @ResultToDict()
        def fn():
            return n

        self.assertEqual(fn(), n)

    @given(st.dictionaries(_STR_KEY, _PRIMITIVE, min_size=1, max_size=5))
    @SETTINGS
    def test_decorator_applies_callback(self, d):
        def cb(results):
            return {'wrapped': results}

        @ResultToDict(callback=cb)
        def fn():
            return d

        result = fn()
        self.assertEqual(result['wrapped'], {str(k): v for k, v in d.items()})

    @given(
        st.dictionaries(_STR_KEY, _PRIMITIVE, min_size=1, max_size=5).filter(
            lambda d: not any(k in d for k in ('a', 'b', 'c'))
        )
    )
    @SETTINGS
    def test_decorator_preserves_function_args(self, d):
        # Filter keeps d disjoint from the function's own arg names so
        # `**d` doesn't override the args we're asserting on.
        @ResultToDict()
        def fn(a, b, c=None):
            return {'a': a, 'b': b, 'c': c, **d}

        result = fn(1, 'x', c=True)
        self.assertEqual(result['a'], 1)
        self.assertEqual(result['b'], 'x')
        self.assertTrue(result['c'])
        for k, v in d.items():
            self.assertEqual(result[k], v)

    def test_decorator_preserves_function_name(self):
        @ResultToDict()
        def my_unique_function_name():
            return {}

        self.assertEqual(my_unique_function_name.__name__, 'my_unique_function_name')
