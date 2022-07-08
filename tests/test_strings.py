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
