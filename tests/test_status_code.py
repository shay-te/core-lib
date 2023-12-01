import unittest

from core_lib.error_handling.status_code_assert import StatusCodeAssert
from core_lib.error_handling.status_code_exception import StatusCodeException


class TestStatusCode(unittest.TestCase):

    def test_status_code_assert(self):
        with self.assertRaises(StatusCodeException):
            with StatusCodeAssert(status_code=500, message="some error occurred"):
                assert True is False
