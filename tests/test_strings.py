import unittest

from core_lib.helpers.string import snake_to_camel, camel_to_snake, any_to_pascal


class TestStrings(unittest.TestCase):
    def test_snake_to_camel(self):
        self.assertEqual(snake_to_camel("this_is_snake_to_camel"), "ThisIsSnakeToCamel")

    def test_camel_to_snake(self):
        self.assertEqual(camel_to_snake("ThisIsCamelToSnake"), "this_is_camel_to_snake")

    def test_any_to_pascal(self):
        self.assertEqual(any_to_pascal('this is pascal'), 'ThisIsPascal')
        self.assertEqual(any_to_pascal('This iS PaScaL'), 'ThisISPaScaL')
        self.assertEqual(any_to_pascal('thisIsPascal'), 'ThisIsPascal')
        self.assertEqual(any_to_pascal('this_is_pascal'), 'ThisIsPascal')
        self.assertEqual(any_to_pascal('ThisIsPascal'), 'ThisIsPascal')
        self.assertEqual(any_to_pascal('this \n\t\r  ------- Is ____pascal'), 'ThisIsPascal')
        self.assertEqual(any_to_pascal('1thi2s_i4s_pasca2l'), 'Thi2sI4sPasca2l')
        self.assertEqual(any_to_pascal('1tHi2s_i4s_5paSca2l'), 'THi2sI4s5paSca2l')
        self.assertEqual(any_to_pascal('this \n\t\r  ----2--- Is ___5_pascal'), 'This2Is5Pascal')


class TestSnakeToCamel(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(snake_to_camel('this_is_snake_to_camel'), 'ThisIsSnakeToCamel')

    def test_single_word(self):
        self.assertEqual(snake_to_camel('hello'), 'Hello')

    def test_already_capitalized(self):
        self.assertEqual(snake_to_camel('Hello_World'), 'HelloWorld')

    def test_multiple_words(self):
        self.assertEqual(snake_to_camel('one_two_three_four'), 'OneTwoThreeFour')

    def test_with_numbers(self):
        self.assertEqual(snake_to_camel('get_user_2_data'), 'GetUser2Data')

    def test_double_underscore(self):
        self.assertEqual(snake_to_camel('a__b'), 'AB')

    def test_leading_underscore(self):
        self.assertEqual(snake_to_camel('_private'), 'Private')

    def test_trailing_underscore(self):
        self.assertEqual(snake_to_camel('name_'), 'Name')

    def test_empty_string(self):
        self.assertEqual(snake_to_camel(''), '')

    def test_already_camel_is_titlecased(self):
        self.assertEqual(snake_to_camel('CamelCase'), 'Camelcase')

    def test_round_trip_with_camel_to_snake(self):
        snake = 'my_cool_function'
        self.assertEqual(camel_to_snake(snake_to_camel(snake)), snake)


class TestCamelToSnake(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(camel_to_snake('ThisIsCamelToSnake'), 'this_is_camel_to_snake')

    def test_single_word_lower(self):
        self.assertEqual(camel_to_snake('hello'), 'hello')

    def test_single_word_upper(self):
        self.assertEqual(camel_to_snake('Hello'), 'hello')

    def test_multiple_words(self):
        self.assertEqual(camel_to_snake('OneTwoThreeFour'), 'one_two_three_four')

    def test_all_caps_each_letter_separated(self):
        # each uppercase letter gets its own underscore prefix
        self.assertEqual(camel_to_snake('HTMLParser'), 'h_t_m_l_parser')

    def test_consecutive_upper_each_separated(self):
        self.assertEqual(camel_to_snake('MyHTMLPage'), 'my_h_t_m_l_page')

    def test_already_snake(self):
        self.assertEqual(camel_to_snake('already_snake'), 'already_snake')

    def test_empty_string(self):
        self.assertEqual(camel_to_snake(''), '')

    def test_single_char_upper(self):
        self.assertEqual(camel_to_snake('A'), 'a')

    def test_single_char_lower(self):
        self.assertEqual(camel_to_snake('a'), 'a')

    def test_no_leading_underscore(self):
        self.assertFalse(camel_to_snake('CamelCase').startswith('_'))

    def test_with_numbers(self):
        result = camel_to_snake('getUser2Data')
        self.assertIn('2', result)
        self.assertIn('user', result)

    def test_output_is_lowercase(self):
        result = camel_to_snake('CamelCaseString')
        self.assertEqual(result, result.lower())


class TestAnyToPascal(unittest.TestCase):
    def test_space_separated(self):
        self.assertEqual(any_to_pascal('this is pascal'), 'ThisIsPascal')

    def test_mixed_case_preserved(self):
        self.assertEqual(any_to_pascal('This iS PaScaL'), 'ThisISPaScaL')

    def test_camel_input(self):
        self.assertEqual(any_to_pascal('thisIsPascal'), 'ThisIsPascal')

    def test_underscore_separated(self):
        self.assertEqual(any_to_pascal('this_is_pascal'), 'ThisIsPascal')

    def test_already_pascal(self):
        self.assertEqual(any_to_pascal('ThisIsPascal'), 'ThisIsPascal')

    def test_mixed_separators_and_whitespace(self):
        self.assertEqual(any_to_pascal('this \n\t\r  ------- Is ____pascal'), 'ThisIsPascal')

    def test_leading_digit_stripped(self):
        self.assertEqual(any_to_pascal('1thi2s_i4s_pasca2l'), 'Thi2sI4sPasca2l')

    def test_leading_digit_uppercase_preserved(self):
        self.assertEqual(any_to_pascal('1tHi2s_i4s_5paSca2l'), 'THi2sI4s5paSca2l')

    def test_numbers_with_separators(self):
        self.assertEqual(any_to_pascal('this \n\t\r  ----2--- Is ___5_pascal'), 'This2Is5Pascal')

    def test_hyphen_separated(self):
        self.assertEqual(any_to_pascal('hello-world'), 'HelloWorld')

    def test_mixed_separators(self):
        self.assertEqual(any_to_pascal('hello-world_foo bar'), 'HelloWorldFooBar')

    def test_numbers_mid_word_kept(self):
        result = any_to_pascal('hello2world')
        self.assertIn('2', result)

    def test_all_caps_word(self):
        result = any_to_pascal('HTML page')
        self.assertIn('HTML', result)

    def test_single_word(self):
        self.assertEqual(any_to_pascal('hello'), 'Hello')

    def test_output_starts_with_upper(self):
        for s in ['hello', 'hello world', 'hello_world', 'helloWorld']:
            result = any_to_pascal(s)
            if result:
                self.assertTrue(result[0].isupper(), f'Expected uppercase start for {s!r}, got {result!r}')

    def test_output_has_no_separators(self):
        result = any_to_pascal('hello_world-foo bar')
        self.assertNotIn('_', result)
        self.assertNotIn('-', result)
        self.assertNotIn(' ', result)
