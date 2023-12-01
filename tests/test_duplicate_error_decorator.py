import unittest

from core_lib.error_handling.duplicate_error_decorator import DuplicateErrorHandler
from core_lib.error_handling.status_code_exception import StatusCodeException
from sqlalchemy import exc

str_value = 'str_value'
tuple_value = ("fruit", "apple")


class TestDuplicateErrorDecorator(unittest.TestCase):

    def test_error_handler(self):
        with self.assertRaises(StatusCodeException):
            self.get_integrity_error()
        self.assertEqual(self.get_string(), str_value)
        self.assertTupleEqual(self.get_tuple(), tuple_value)

    @DuplicateErrorHandler()
    def get_integrity_error(self):
        raise exc.IntegrityError("Simulated IntegrityError", {}, None)

    @DuplicateErrorHandler()
    def get_string(self):
        return str_value

    @DuplicateErrorHandler()
    def get_tuple(self):
        return tuple_value


