import json
import unittest
from http import HTTPStatus

from django.conf import settings

from core_lib.error_handling.status_code_assert import StatusCodeAssert
from core_lib.error_handling.status_code_exception import StatusCodeException
from core_lib.web_helpers.decorators import handle_exceptions
from core_lib.web_helpers.request_response_helpers import response_json
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils

settings.configure()
settings.DEFAULT_CHARSET = 'utf-8'


class TestHandleExceptions(unittest.TestCase):

    def test_raises_exception(self):
        web_util = WebHelpersUtils()
        web_util.init(web_util.ServerType.DJANGO)

        print(self.get_data())

    @handle_exceptions
    def get_data(self):
        return response_json()
