import unittest

from core_lib.error_handling.not_found_decorator import NotFoundErrorHandler
from core_lib.error_handling.status_code_exception import StatusCodeException

str_value = 'str_value'
tuple_value = ("fruit", "apple")


class TestNotFoundErrorDecorator(unittest.TestCase):

    def test_error_handler(self):
        with self.assertRaises(StatusCodeException):
            self.get_nothing()
        self.assertEqual(self.get_string(), str_value)
        self.assertTupleEqual(self.get_tuple(), tuple_value)

    @NotFoundErrorHandler()
    def get_string(self):
        return str_value

    @NotFoundErrorHandler()
    def get_tuple(self):
        return tuple_value

    @NotFoundErrorHandler()
    def get_nothing(self):
        # check that it raises not found error
        pass
