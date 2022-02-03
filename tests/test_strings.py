import unittest

from core_lib.helpers.string import snake_to_camel, camel_to_snake


class TestStrings(unittest.TestCase):

    def test_snake_to_camel(self):
        self.assertEqual(snake_to_camel("this_is_snake_to_camel"), "ThisIsSnakeToCamel")

    def test_camel_to_snake(self):
        self.assertEqual(camel_to_snake("ThisIsCamelToSnake"), "this_is_camel_to_snake")
