import unittest

from core_lib.error_handling.not_found_decorator import NotFoundErrorHandler
from core_lib.error_handling.status_code_assert import StatusCodeAssert
from core_lib.error_handling.status_code_exception import StatusCodeException

str_value = 'str_value'
tuple_value = ("fruit", "apple")


class TestErrorHandling(unittest.TestCase):
    def test_error_handler_string(self):
        with self.assertRaises(StatusCodeException):
            self.get_nothing()

        self.assertEqual(self.get_string(), str_value)

    def test_error_handler_tuple(self):
        with self.assertRaises(StatusCodeException):
            self.get_nothing()

        self.assertTupleEqual(self.get_tuple(), tuple_value)

    def test_status_code_assert(self):
        with self.assertRaises(StatusCodeException):
            with StatusCodeAssert(status_code=500, message="some error occurred"):
                assert True is False

    @NotFoundErrorHandler()
    def get_string(self):
        return str_value

    @NotFoundErrorHandler()
    def get_tuple(self):
        return tuple_value

    @NotFoundErrorHandler()
    def get_nothing(self):
        pass
