import unittest

from core_lib.helpers.string import snake_to_camel, camel_to_snake


class TestStrings(unittest.TestCase):

    def test_snake_to_camel(self):
        self.assertNotEqual(snake_to_camel("hello_world"), None)
        self.assertEqual(snake_to_camel("hello_world"), "HelloWorld")
        self.assertNotEqual(snake_to_camel("this_is_snake_to_camel"), None)
        self.assertEqual(snake_to_camel("this_is_snake_to_camel"), "ThisIsSnakeToCamel")

    def test_camel_to_snake(self):
        self.assertNotEqual(camel_to_snake("HelloWorld"), None)
        self.assertEqual(camel_to_snake("HelloWorld"), "hello_world")
        self.assertNotEqual(camel_to_snake("ThisIsCamelToSnake"), None)
        self.assertEqual(camel_to_snake("ThisIsCamelToSnake"), "this_is_camel_to_snake")
