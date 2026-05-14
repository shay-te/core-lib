"""Edge-case / challenge tests for utility functions.

Coverage-by-execution is fine, but utilities deserve to be hit with awkward
inputs and full flag-permutation combos. These tests target gaps that the
existing per-module tests don't cover.
"""
import datetime
import unittest

from core_lib.helpers.parse_utils import (
    clean_list,
    find_key_by_value,
    float_to_str,
    parse_any_nan,
    parse_bool,
    parse_date,
    parse_range,
)
from core_lib.helpers.func_utils import (
    build_function_key,
    get_func_parameter_index_by_name,
    get_func_parameters_as_dict,
    UnseenFormatter,
)
from core_lib.helpers.string import any_to_pascal, camel_to_snake, snake_to_camel
from core_lib.data_layers.data.data_helpers import build_url


# ── parse_date: all 10 supported formats explicitly ─────────────────────────


class TestParseDateAllFormats(unittest.TestCase):
    def test_format_mdy_hms_pm(self):
        dt = parse_date('12/25/2024 3:30:45 pm')
        self.assertEqual(dt, datetime.datetime(2024, 12, 25, 15, 30, 45))

    def test_format_mdy_hm_am(self):
        dt = parse_date('1/2/2024 11:30 am')
        self.assertEqual(dt, datetime.datetime(2024, 1, 2, 11, 30))

    def test_format_mdy(self):
        dt = parse_date('06/15/2024')
        self.assertEqual(dt, datetime.datetime(2024, 6, 15))

    def test_format_b_d_y(self):
        dt = parse_date('Jun 15, 2024')
        self.assertEqual(dt, datetime.datetime(2024, 6, 15))

    def test_format_full_month_d_y(self):
        dt = parse_date('June 15, 2024')
        self.assertEqual(dt, datetime.datetime(2024, 6, 15))

    def test_format_y_m_d_slash(self):
        dt = parse_date('2024/06/15')
        self.assertEqual(dt, datetime.datetime(2024, 6, 15))

    def test_format_y_m_d_dash(self):
        dt = parse_date('2024-06-15')
        self.assertEqual(dt, datetime.datetime(2024, 6, 15))

    def test_format_d_m_y_dash(self):
        # NOTE: ambiguous with mdy; this parses as 15-06-2024 → 15 June 2024.
        # Picking values where mdy fails so this format is required.
        dt = parse_date('25-06-2024')
        self.assertEqual(dt, datetime.datetime(2024, 6, 25))

    def test_format_y_m_d_dot(self):
        dt = parse_date('2024.06.15')
        self.assertEqual(dt, datetime.datetime(2024, 6, 15))

    def test_format_d_m_y_dot(self):
        dt = parse_date('25.06.2024')
        self.assertEqual(dt, datetime.datetime(2024, 6, 25))

    def test_misspelled_month_normalization(self):
        # "Janu" → "jan", etc.
        self.assertEqual(parse_date('Janu 12, 2024'), datetime.datetime(2024, 1, 12))
        self.assertEqual(parse_date('Febr 12, 2024'), datetime.datetime(2024, 2, 12))
        self.assertEqual(parse_date('Marc 12, 2024'), datetime.datetime(2024, 3, 12))
        self.assertEqual(parse_date('Apri 12, 2024'), datetime.datetime(2024, 4, 12))

    def test_whitespace_normalization_around_separators(self):
        # The function collapses whitespace and tightens ', ' and ' / '
        self.assertIsNotNone(parse_date('Jun  15  ,  2024'))
        self.assertIsNotNone(parse_date('06 / 15 / 2024'))


# ── parse_range: all flag combos and edge inputs ────────────────────────────


class TestParseRangeChallenges(unittest.TestCase):
    def test_non_string(self):
        self.assertIsNone(parse_range(None))
        self.assertIsNone(parse_range(42))
        self.assertIsNone(parse_range(['x', 'y']))

    def test_no_to_separator(self):
        self.assertIsNone(parse_range('10 20'))
        self.assertIsNone(parse_range('-'))

    def test_empty_components(self):
        self.assertIsNone(parse_range(''))
        self.assertIsNone(parse_range('to'))
        self.assertIsNone(parse_range('10 to'))
        self.assertIsNone(parse_range('to 10'))

    def test_case_insensitive(self):
        # parse_range does .lower() internally
        self.assertEqual(parse_range('1 TO 5'), (1, 5))
        self.assertEqual(parse_range('Any to 5', min_limit=0), (0, 5))

    def test_negative_numbers_not_parsed_as_int(self):
        # '-5'.isdigit() is False — so -5 falls through to the raw-string branch.
        result = parse_range('-5 to 5')
        self.assertEqual(result, ('-5', 5))


# ── parse_bool: every documented true/false token ──────────────────────────


class TestParseBoolChallenges(unittest.TestCase):
    def test_string_true_tokens(self):
        for token in ['yes', 'true', '1', 'YES', 'True', 'TRUE', ' yes ', ' true ']:
            with self.subTest(token=token):
                self.assertTrue(parse_bool(token))

    def test_string_false_tokens(self):
        for token in ['no', 'false', '0', 'NO', 'False', 'FALSE', ' no ', ' false ']:
            with self.subTest(token=token):
                self.assertFalse(parse_bool(token))

    def test_integer_one_zero(self):
        self.assertTrue(parse_bool(1))
        self.assertFalse(parse_bool(0))

    def test_integer_other_returns_none(self):
        for v in [2, -1, 100, -100]:
            with self.subTest(v=v):
                self.assertIsNone(parse_bool(v))

    def test_bool_passthrough(self):
        self.assertTrue(parse_bool(True))
        self.assertFalse(parse_bool(False))

    def test_misc_types_return_none(self):
        for v in [None, 1.0, 'maybe', {}, [], object()]:
            with self.subTest(v=v):
                self.assertIsNone(parse_bool(v))


# ── parse_any_nan: strings_to_replace combinations ─────────────────────────


class TestParseAnyNanChallenges(unittest.TestCase):
    def test_default_strings_to_replace_empty(self):
        self.assertEqual(parse_any_nan('nan'), 'nan')

    def test_custom_strings_to_replace(self):
        self.assertIsNone(parse_any_nan('nan', strings_to_replace=('nan',)))
        self.assertIsNone(parse_any_nan('NULL', strings_to_replace=('null',)))
        self.assertIsNone(parse_any_nan('  none  ', strings_to_replace=('none',)))

    def test_replace_with_value(self):
        self.assertEqual(
            parse_any_nan('nan', replace_with='DEFAULT', strings_to_replace=('nan',)),
            'DEFAULT',
        )

    def test_passthrough_non_matching(self):
        self.assertEqual(parse_any_nan('hello', strings_to_replace=('nan',)), 'hello')

    def test_list_recursion(self):
        self.assertEqual(
            parse_any_nan(['ok', 'nan'], strings_to_replace=('nan',)),
            ['ok', None],
        )


# ── float_to_str: every branch with extreme values ─────────────────────────


class TestFloatToStrChallenges(unittest.TestCase):
    def test_none_returns_empty(self):
        self.assertEqual(float_to_str(None), '')

    def test_nan_returns_empty(self):
        self.assertEqual(float_to_str(float('nan')), '')

    def test_integer_valued_float(self):
        self.assertEqual(float_to_str(5.0), '5')
        self.assertEqual(float_to_str(-3.0), '-3')

    def test_non_integer_float(self):
        self.assertEqual(float_to_str(3.14), '3.14')

    def test_remove_dot_with_non_integer(self):
        self.assertEqual(float_to_str(3.14, remove_dot=True), '314')

    def test_remove_dot_with_integer_valued(self):
        # Integer-valued floats skip the remove_dot path
        self.assertEqual(float_to_str(5.0, remove_dot=True), '5')

    def test_string_passthrough(self):
        self.assertEqual(float_to_str('abc'), 'abc')

    def test_int_passthrough(self):
        self.assertEqual(float_to_str(5), '5')

    def test_extreme_values(self):
        self.assertEqual(float_to_str(0.0), '0')
        self.assertEqual(float_to_str(-0.0), '0')


# ── clean_list ─────────────────────────────────────────────────────────────


class TestCleanListChallenges(unittest.TestCase):
    def test_non_list_returns_empty(self):
        self.assertEqual(clean_list(None), [])
        self.assertEqual(clean_list('not a list'), [])
        self.assertEqual(clean_list({'k': 'v'}), [])

    def test_filters_falsy_collection_types(self):
        self.assertEqual(clean_list([1, '', None, [], {}, ()]), [1])

    def test_preserves_truthy_falsy(self):
        # 0 and False are NOT filtered because they're not in the explicit
        # `(None, "", [], {}, ())` tuple.
        self.assertEqual(clean_list([0, False]), [0, False])

    def test_preserves_all_truthy(self):
        self.assertEqual(clean_list([1, 'a', [1], {'k': 'v'}]), [1, 'a', [1], {'k': 'v'}])


# ── find_key_by_value ──────────────────────────────────────────────────────


class TestFindKeyByValueChallenges(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(find_key_by_value({'a': 1, 'b': 2}, 2), 'b')

    def test_missing_returns_none(self):
        self.assertIsNone(find_key_by_value({'a': 1}, 99))

    def test_empty_dict(self):
        self.assertIsNone(find_key_by_value({}, 'anything'))

    def test_returns_first_match(self):
        # Dicts preserve insertion order in Py3.7+ so this is deterministic
        d = {'a': 1, 'b': 1, 'c': 1}
        self.assertEqual(find_key_by_value(d, 1), 'a')

    def test_none_value(self):
        self.assertEqual(find_key_by_value({'a': None, 'b': 1}, None), 'a')


# ── func_utils: build_function_key edges ───────────────────────────────────


class TestFuncUtilsChallenges(unittest.TestCase):
    def test_get_func_parameter_index(self):
        def f(a, b, c):
            pass  # intentionally empty
        self.assertEqual(get_func_parameter_index_by_name(f, 'a'), 0)
        self.assertEqual(get_func_parameter_index_by_name(f, 'c'), 2)

    def test_get_func_parameter_index_missing(self):
        def f(a):
            pass  # intentionally empty
        with self.assertRaises(ValueError):
            get_func_parameter_index_by_name(f, 'nope')

    def test_get_func_parameters_as_dict_defaults(self):
        def f(a, b=2, c=3):
            pass  # intentionally empty
        d = get_func_parameters_as_dict(f, 1)
        self.assertEqual(d, {'a': 1, 'b': 2, 'c': 3})

    def test_get_func_parameters_kwargs_override(self):
        def f(a, b=2):
            pass  # intentionally empty
        d = get_func_parameters_as_dict(f, 10, b=20)
        self.assertEqual(d, {'a': 10, 'b': 20})

    def test_get_func_parameters_no_value(self):
        def f(a):
            pass  # intentionally empty
        d = get_func_parameters_as_dict(f)
        self.assertEqual(d, {'a': None})

    def test_build_function_key_strips_newlines_and_returns(self):
        def f(a):
            pass  # intentionally empty
        # Inject \n via key formatting
        result = build_function_key('k-{a}', f, 'value\nwith\rcontrol')
        self.assertNotIn('\n', result)
        self.assertNotIn('\r', result)

    def test_unseen_formatter_keyable_falsy_marker(self):
        f = UnseenFormatter()
        # Force the empty-value path of _get_key_value via the exception handler
        class Bad:
            def __getitem__(self, k):
                raise RuntimeError('boom')

        # When the formatter passes a string key into a "dict" that raises,
        # the exception is caught and returns !EkE!
        result = f.format('{foo}', foo=None)
        # foo is None → _get_key_value returns the marker
        self.assertEqual(result, '!EfooE!')


# ── string helpers: edges ──────────────────────────────────────────────────


class TestStringHelpersChallenges(unittest.TestCase):
    def test_snake_to_camel_empty_string(self):
        self.assertEqual(snake_to_camel(''), '')

    def test_snake_to_camel_already_camel(self):
        # snake_to_camel preserves non-underscore chars but Title-cases each token
        result = snake_to_camel('foo')
        self.assertEqual(result, 'Foo')

    def test_camel_to_snake_single_uppercase(self):
        self.assertEqual(camel_to_snake('A'), 'a')

    def test_camel_to_snake_no_uppercase(self):
        self.assertEqual(camel_to_snake('foo'), 'foo')

    def test_any_to_pascal_unicode_letters(self):
        # Non-ASCII characters are kept verbatim in current implementation.
        # We just want to assert no exception.
        try:
            any_to_pascal('héllo world')
        except Exception as e:
            self.fail(f'any_to_pascal raised on unicode: {e}')


# ── build_url: every parameter combination ─────────────────────────────────


class TestBuildUrlChallenges(unittest.TestCase):
    def test_empty_returns_empty(self):
        self.assertEqual(build_url(), '')

    def test_protocol_only(self):
        self.assertEqual(build_url(protocol='http'), 'http://')

    def test_with_username_no_password(self):
        self.assertEqual(
            build_url(protocol='proto', username='u', host='h'),
            'proto://u@h',
        )

    def test_with_username_and_password(self):
        # NOSONAR — "p" is a URL-builder fixture, not a real credential.
        self.assertEqual(
            build_url(protocol='proto', username='u', password='p', host='h'),  # NOSONAR
            'proto://u:p@h',
        )

    def test_password_without_username_inserts_at_sign(self):
        self.assertEqual(
            build_url(protocol='proto', password='p', host='h'),  # NOSONAR — fixture, not a credential.
            'proto://@h',
        )

    def test_host_and_port(self):
        self.assertEqual(build_url(host='h', port=80), 'h:80')

    def test_path_normalizes_leading_slash(self):
        # Always exactly one leading slash before the path segment.
        self.assertEqual(build_url(host='h', path='/a/b'), 'h/a/b')
        self.assertEqual(build_url(host='h', path='a/b'), 'h/a/b')
        self.assertEqual(build_url(host='h', path='///a/b'), 'h/a/b')

    def test_file_normalizes_leading_slash(self):
        self.assertEqual(build_url(host='h', file='/file.db'), 'h/file.db')
        self.assertEqual(build_url(host='h', file='file.db'), 'h/file.db')

    def test_kwargs_ignored(self):
        # Extra kwargs are accepted but ignored (the function uses *args/**kwargs)
        self.assertEqual(
            build_url(protocol='http', host='h', extra_field='ignored'),
            'http://h',
        )

    def test_full_url(self):
        self.assertEqual(
            build_url(
                protocol='postgres',
                username='u',
                password='p',  # NOSONAR — URL-builder fixture, not a credential.
                host='h',
                port=5432,
                path='mydb',
            ),
            'postgres://u:p@h:5432/mydb',
        )
