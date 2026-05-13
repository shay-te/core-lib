"""Property-based tests for helpers.func_utils."""
import string as stringmod
import unittest

from hypothesis import given, strategies as st

from core_lib.helpers.func_utils import (
    UnseenFormatter,
    build_function_key,
    get_func_parameter_index_by_name,
    get_func_parameters_as_dict,
)
from tests.hypothesis_tests._settings import SETTINGS


class TestUnseenFormatterProperties(unittest.TestCase):
    @given(value=st.text(min_size=1, max_size=20))
    @SETTINGS
    def test_present_kwarg_substitutes_value(self, value):
        f = UnseenFormatter()
        result = f.format('{k}', k=value)
        self.assertEqual(result, value)

    @given(missing=st.text(alphabet=stringmod.ascii_letters, min_size=1, max_size=10))
    @SETTINGS
    def test_missing_kwarg_uses_marker(self, missing):
        f = UnseenFormatter()
        result = f.format('{' + missing + '}')
        self.assertEqual(result, f'!M{missing}M!')

    @given(value=st.text(min_size=1, max_size=20))
    @SETTINGS
    def test_positional_arg_substitutes_value(self, value):
        f = UnseenFormatter()
        result = f.format('{0}', value)
        self.assertEqual(result, value)


class TestGetFuncParamsProperties(unittest.TestCase):
    @given(n=st.integers(min_value=1, max_value=10))
    @SETTINGS
    def test_param_index_matches_position(self, n):
        # Build a function with n params named p0..p(n-1)
        param_names = [f'p{i}' for i in range(n)]
        source = f"def f({', '.join(param_names)}): pass"
        namespace = {}
        exec(source, namespace)
        f = namespace['f']
        for i, name in enumerate(param_names):
            self.assertEqual(get_func_parameter_index_by_name(f, name), i)

    @given(values=st.lists(st.integers(), min_size=1, max_size=5))
    @SETTINGS
    def test_params_as_dict_captures_positional(self, values):
        n = len(values)
        param_names = [f'p{i}' for i in range(n)]
        source = f"def f({', '.join(param_names)}): pass"
        namespace = {}
        exec(source, namespace)
        f = namespace['f']
        d = get_func_parameters_as_dict(f, *values)
        for name, val in zip(param_names, values):
            self.assertEqual(d[name], val)


class TestBuildFunctionKeyProperties(unittest.TestCase):
    @given(
        value=st.text(
            alphabet=stringmod.ascii_letters + '\n\r',
            min_size=1,
            max_size=20,
        )
    )
    @SETTINGS
    def test_result_never_contains_newlines_or_returns(self, value):
        def f(x):
            pass
        result = build_function_key('k-{x}', f, value)
        self.assertNotIn('\n', result)
        self.assertNotIn('\r', result)

    @given(name=st.text(alphabet=stringmod.ascii_letters, min_size=1, max_size=10))
    @SETTINGS
    def test_empty_key_uses_qualname(self, name):
        # Build a function dynamically so its qualname includes the random name
        def f():
            pass
        f.__qualname__ = name
        result = build_function_key(None, f)
        self.assertEqual(result, name)
