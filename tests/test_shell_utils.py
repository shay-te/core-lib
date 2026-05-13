import enum
import unittest
from io import StringIO
from unittest.mock import patch

from core_lib.helpers.shell_utils import (
    _coalesce_prompt_value,
    _empty_prompt_result,
    _format,
    prompt_bool,
    prompt_comma_list,
    prompt_email,
    prompt_enum,
    prompt_file_name,
    prompt_int,
    prompt_list,
    prompt_options,
    prompt_str,
    prompt_string,
    prompt_timeframe,
    prompt_url,
    prompt_yes_no,
)


class _Color(enum.Enum):
    RED = 1
    BLUE = 2


def _inputs(*values):
    """Patch input with a queue of values to consume."""
    iterator = iter(values)

    def fake_input(_):
        return next(iterator)

    return fake_input


class TestPrivateHelpers(unittest.TestCase):
    def test_format_with_default(self):
        self.assertEqual(_format('Name', default='x'), 'Name [default: x]: ')

    def test_format_with_allow_none(self):
        self.assertEqual(_format('Name', allow_none=True), 'Name [press Enter to skip]: ')

    def test_format_plain(self):
        self.assertEqual(_format('Name'), 'Name: ')

    def test_empty_prompt_result_default(self):
        self.assertEqual(_empty_prompt_result(default='d'), 'd')

    def test_empty_prompt_result_none(self):
        self.assertIsNone(_empty_prompt_result(allow_none=True))

    def test_empty_prompt_result_empty(self):
        self.assertEqual(_empty_prompt_result(allow_empty=True), '')

    def test_empty_prompt_result_fallback(self):
        self.assertIsNone(_empty_prompt_result())

    def test_coalesce_prompt_value_raw(self):
        self.assertEqual(_coalesce_prompt_value('x', None), 'x')

    def test_coalesce_prompt_value_default(self):
        self.assertEqual(_coalesce_prompt_value('', 5), '5')

    def test_coalesce_prompt_value_empty(self):
        self.assertEqual(_coalesce_prompt_value('', None), '')


class TestPrompts(unittest.TestCase):
    def test_prompt_string_retries_until_value(self):
        with patch('builtins.input', _inputs('', 'final')):
            self.assertEqual(prompt_string('q'), 'final')

    def test_prompt_str_with_validation_failure_then_success(self):
        with patch('builtins.input', _inputs('bad', 'good')):
            self.assertEqual(prompt_str('q', validate_callback=lambda v: v == 'good'), 'good')

    def test_prompt_str_with_default(self):
        with patch('builtins.input', _inputs('')):
            self.assertEqual(prompt_str('q', default='def'), 'def')

    def test_prompt_str_allow_none(self):
        with patch('builtins.input', _inputs('')):
            self.assertIsNone(prompt_str('q', allow_none=True))

    def test_prompt_str_allow_empty(self):
        with patch('builtins.input', _inputs('')):
            self.assertEqual(prompt_str('q', allow_empty=True), '')

    def test_prompt_str_retries_on_empty(self):
        with patch('builtins.input', _inputs('', 'value')):
            self.assertEqual(prompt_str('q'), 'value')

    def test_prompt_file_name_strips_unsafe(self):
        with patch('builtins.input', _inputs('!!!', 'my-file-1')):
            self.assertEqual(prompt_file_name('q'), 'my_file_')

    def test_prompt_yes_no_yes(self):
        with patch('builtins.input', _inputs('yes')):
            self.assertTrue(prompt_yes_no('q'))

    def test_prompt_yes_no_no(self):
        with patch('builtins.input', _inputs('n')):
            self.assertFalse(prompt_yes_no('q'))

    def test_prompt_yes_no_with_default_true(self):
        with patch('builtins.input', _inputs('')):
            self.assertTrue(prompt_yes_no('q', default=True))

    def test_prompt_yes_no_with_default_false(self):
        with patch('builtins.input', _inputs('')):
            self.assertFalse(prompt_yes_no('q', default=False))

    def test_prompt_yes_no_retries(self):
        with patch('builtins.input', _inputs('huh', 'yes')):
            self.assertTrue(prompt_yes_no('q'))

    def test_prompt_bool_true_1(self):
        with patch('builtins.input', _inputs('1')):
            self.assertTrue(prompt_bool('q'))

    def test_prompt_bool_false_0(self):
        with patch('builtins.input', _inputs('0')):
            self.assertFalse(prompt_bool('q'))

    def test_prompt_bool_default_true(self):
        with patch('builtins.input', _inputs('')):
            self.assertTrue(prompt_bool('q', default=True))

    def test_prompt_bool_allow_none(self):
        with patch('builtins.input', _inputs('')):
            self.assertIsNone(prompt_bool('q', allow_none=True))

    def test_prompt_bool_retries(self):
        with patch('builtins.input', _inputs('', 'true')):
            self.assertTrue(prompt_bool('q'))

    def test_prompt_int_default(self):
        with patch('builtins.input', _inputs('')):
            self.assertEqual(prompt_int('q', default=42), 42)

    def test_prompt_int_allow_none(self):
        with patch('builtins.input', _inputs('')):
            self.assertIsNone(prompt_int('q', allow_none=True))

    def test_prompt_int_retries_on_invalid(self):
        with patch('builtins.input', _inputs('abc', '7')):
            self.assertEqual(prompt_int('q'), 7)

    def test_prompt_int_retries_on_empty(self):
        with patch('builtins.input', _inputs('', '7')):
            self.assertEqual(prompt_int('q'), 7)

    def test_prompt_email_default_used(self):
        with patch('builtins.input', _inputs('')):
            self.assertEqual(prompt_email('q', default='a@b.com'), 'a@b.com')

    def test_prompt_email_invalid_then_valid(self):
        with patch('builtins.input', _inputs('not-an-email', 'good@example.com')):
            self.assertEqual(prompt_email('q'), 'good@example.com')

    def test_prompt_url_allow_empty(self):
        with patch('builtins.input', _inputs('')):
            self.assertEqual(prompt_url('q', allow_empty=True), '')

    def test_prompt_url_invalid_then_valid(self):
        with patch('builtins.input', _inputs('nope', 'http://example.com')):
            self.assertEqual(prompt_url('q'), 'http://example.com')

    def test_prompt_timeframe_boot(self):
        with patch('builtins.input', _inputs('boot')):
            self.assertEqual(prompt_timeframe('q'), '0s')

    def test_prompt_timeframe_allow_empty(self):
        with patch('builtins.input', _inputs('')):
            self.assertEqual(prompt_timeframe('q', allow_empty=True), '')

    def test_prompt_timeframe_valid_value(self):
        with patch('builtins.input', _inputs('1h30m')):
            self.assertEqual(prompt_timeframe('q'), '1h30m')

    def test_prompt_timeframe_invalid_then_valid(self):
        with patch('builtins.input', _inputs('nope', '5s')):
            self.assertEqual(prompt_timeframe('q'), '5s')

    def test_prompt_enum_with_default(self):
        with patch('builtins.input', _inputs('')):
            self.assertEqual(prompt_enum(_Color, 'q', default=1), 1)

    def test_prompt_enum_invalid_then_valid(self):
        with patch('builtins.input', _inputs('99', '2')):
            self.assertEqual(prompt_enum(_Color, 'q'), 2)


class TestPromptOptions(unittest.TestCase):
    def test_empty_options_raises(self):
        with self.assertRaises(ValueError):
            prompt_options('msg', [])

    def test_default_not_in_options_raises(self):
        with self.assertRaises(ValueError):
            prompt_options('msg', ['a', 'b'], default='c')

    def test_default_picked_on_empty_input(self):
        with patch('builtins.input', _inputs('')):
            self.assertEqual(prompt_options('msg', ['a', 'b'], default='a'), 'a')

    def test_pick_by_number(self):
        with patch('builtins.input', _inputs('2')):
            self.assertEqual(prompt_options('msg', ['a', 'b']), 'b')

    def test_invalid_then_valid(self):
        with patch('builtins.input', _inputs('99', '1')):
            self.assertEqual(prompt_options('msg', ['a', 'b']), 'a')


class TestPromptList(unittest.TestCase):
    def test_pick_index(self):
        with patch('builtins.input', _inputs('2')):
            self.assertEqual(prompt_list(['a', 'b', 'c'], 'q'), 1)

    def test_validate_failure_then_success(self):
        validator = lambda val: val != 'a'
        with patch('builtins.input', _inputs('1', '2')):
            self.assertEqual(prompt_list(['a', 'b'], 'q', validate_callback=validator), 1)

    def test_invalid_then_valid(self):
        with patch('builtins.input', _inputs('foo', '1')):
            self.assertEqual(prompt_list(['a', 'b'], 'q'), 0)


class TestPromptCommaList(unittest.TestCase):
    def test_default_used(self):
        with patch('builtins.input', _inputs('')):
            self.assertEqual(prompt_comma_list('q', default=['x']), ['x'])

    def test_allow_empty(self):
        with patch('builtins.input', _inputs('')):
            self.assertEqual(prompt_comma_list('q'), [])

    def test_parses_values(self):
        with patch('builtins.input', _inputs('a, b, c')):
            self.assertEqual(prompt_comma_list('q'), ['a', 'b', 'c'])

    def test_value_parser_raises_then_succeeds(self):
        def parser(v):
            if v == 'bad':
                raise ValueError('no')
            return v

        with patch('builtins.input', _inputs('bad', 'good')):
            self.assertEqual(prompt_comma_list('q', value_parser=parser), ['good'])

    def test_empty_parsed_when_not_allow_empty_retries(self):
        # allow_empty=False and parser returns [] should retry until non-empty
        with patch('builtins.input', _inputs('a')):
            self.assertEqual(
                prompt_comma_list('q', allow_empty=False),
                ['a'],
            )
