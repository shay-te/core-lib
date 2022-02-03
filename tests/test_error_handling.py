import unittest

from core_lib.error_handling.not_found_decorator import NotFoundErrorHandler
from core_lib.error_handling.status_code_assert import StatusCodeAssert


class TestErrorHandling(unittest.TestCase):

    def test_error_handler_string(self):
        with self.assertRaises(Exception):
            self.get_string(True)

        self.assertEqual(self.get_string(False), "no exception")

    def test_error_handler_tuple(self):
        with self.assertRaises(Exception):
            self.get_tuple(True)

        self.assertEqual(self.get_tuple(False), ("fruit", "apple"))

    def test_status_code_assert(self):
        with self.assertRaises(AssertionError):
            StatusCodeAssert(status_code=500, message="some error occured")

    @NotFoundErrorHandler()
    def get_string(self, excp):
        if excp:
            pass
        else:
            return "no exception"

    @NotFoundErrorHandler()
    def get_tuple(self, excp):
        if excp:
            pass
        else:
            return ("fruit", "apple")