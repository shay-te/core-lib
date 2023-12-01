import unittest

from core_lib.error_handling.duplicate_error_decorator import DuplicateErrorHandler
from core_lib.error_handling.not_found_decorator import NotFoundErrorHandler
from core_lib.error_handling.status_code_assert import StatusCodeAssert
from core_lib.error_handling.status_code_exception import StatusCodeException
from sqlalchemy import exc

str_value = 'str_value'
tuple_value = ("fruit", "apple")


class TestErrorHandling(unittest.TestCase):
    def test_not_found_error_handler_string(self):
        with self.assertRaises(StatusCodeException):
            self.get_nothing_with_not_found_error_handler()

        self.assertEqual(self.get_string_with_not_found_error_handler(), str_value)

    def test_not_found_error_handler_tuple(self):
        with self.assertRaises(StatusCodeException):
            self.get_nothing_with_not_found_error_handler()

        self.assertTupleEqual(self.get_tuple_with_not_found_error_handler(), tuple_value)

    def test_duplicate_error_handler_string(self):
        with self.assertRaises(StatusCodeException):
            self.get_integrity_error_with_duplicate_error_handler()

        self.assertEqual(self.get_string_with_duplicate_error_handler(), str_value)

    def test_duplicate_error_handler_tuple(self):
        with self.assertRaises(StatusCodeException):
            self.get_integrity_error_with_duplicate_error_handler()

        self.assertTupleEqual(self.get_tuple_with_duplicate_error_handler(), tuple_value)

    def test_status_code_assert(self):
        with self.assertRaises(StatusCodeException):
            with StatusCodeAssert(status_code=500, message="some error occurred"):
                assert True is False

    @NotFoundErrorHandler()
    def get_string_with_not_found_error_handler(self):
        return str_value

    @NotFoundErrorHandler()
    def get_tuple_with_not_found_error_handler(self):
        return tuple_value

    @NotFoundErrorHandler()
    def get_nothing_with_not_found_error_handler(self):
        # Method is empty to check that it raises not found error
        pass

    @DuplicateErrorHandler()
    def get_integrity_error_with_duplicate_error_handler(self):
        raise exc.IntegrityError("Simulated IntegrityError", {}, None)

    @DuplicateErrorHandler()
    def get_string_with_duplicate_error_handler(self):
        return str_value

    @DuplicateErrorHandler()
    def get_tuple_with_duplicate_error_handler(self):
        return tuple_value


