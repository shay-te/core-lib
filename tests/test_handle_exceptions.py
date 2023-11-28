import json
import unittest
from http import HTTPStatus

from django.conf import settings

from core_lib.error_handling.status_code_exception import StatusCodeException
from core_lib.web_helpers.decorators import HandleException
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils

if not settings.configured:
    settings.configure()
    settings.DEFAULT_CHARSET = 'utf-8'


class TestHandleException(unittest.TestCase):
    def test_raises_exception_django(self):
        web_util = WebHelpersUtils()
        web_util.init(web_util.ServerType.DJANGO)

        with self.assertLogs() as cm:
            resp_json = self.raise_exception(BaseException)
            self.assertEqual(resp_json.status_code, 500)
            resp_json_data = json.loads(resp_json.content.decode('utf-8'))
            self.assertIsInstance(resp_json_data, dict)
            self.assertEqual(resp_json_data['error'], 'Internal Server Error')
            self.assertIn('BaseException', str(cm.output))
            self.assertIn('handle_exception got BaseException error for function', str(cm.output))

        with self.assertLogs() as cm:
            resp_json = self.raise_exception(AssertionError)
            self.assertEqual(resp_json.status_code, 500)
            resp_json_data = json.loads(resp_json.content.decode('utf-8'))
            self.assertIsInstance(resp_json_data, dict)
            self.assertEqual(resp_json_data['error'], 'Internal Server Error')
            self.assertIn('AssertionError', str(cm.output))
            self.assertIn('handle_exception got AssertionError error for function', str(cm.output))

        with self.assertLogs() as cm:
            resp_json = self.raise_exception(StatusCodeException(HTTPStatus.NOT_FOUND))
            self.assertEqual(resp_json.status_code, 404)
            resp_json_data = json.loads(resp_json.content.decode('utf-8'))
            self.assertIsInstance(resp_json_data, dict)
            self.assertEqual(resp_json_data['message'], 'Not Found')
            self.assertIn('StatusCodeException', str(cm.output))
            self.assertIn('handle_exception got StatusCodeException error for function', str(cm.output))

        with self.assertLogs() as cm:
            resp_json = self.raise_assertion()
            self.assertEqual(resp_json.status_code, 500)
            resp_json_data = json.loads(resp_json.content.decode('utf-8'))
            self.assertIsInstance(resp_json_data, dict)
            self.assertEqual(resp_json_data['error'], 'Internal Server Error')
            self.assertIn('AssertionError', str(cm.output))
            self.assertIn('handle_exception got AssertionError error for function', str(cm.output))

    def test_raises_exception_flask(self):
        web_util = WebHelpersUtils()
        web_util.init(web_util.ServerType.FLASK)

        with self.assertLogs() as cm:
            resp_json = self.raise_exception(BaseException)
            self.assertEqual(resp_json.status_code, 500)
            self.assertEqual(resp_json.status, "500 INTERNAL SERVER ERROR")
            resp_msg_data = json.loads(resp_json.data.decode('utf-8'))
            self.assertIsInstance(resp_msg_data, dict)
            self.assertEqual(resp_msg_data['error'], 'Internal Server Error')
            self.assertIn('BaseException', str(cm.output))
            self.assertIn('handle_exception got BaseException error for function', str(cm.output))

        with self.assertLogs() as cm:
            resp_json = self.raise_exception(AssertionError)
            self.assertEqual(resp_json.status_code, 500)
            self.assertEqual(resp_json.status, "500 INTERNAL SERVER ERROR")
            resp_msg_data = json.loads(resp_json.data.decode('utf-8'))
            self.assertIsInstance(resp_msg_data, dict)
            self.assertEqual(resp_msg_data['error'], 'Internal Server Error')
            self.assertIn('AssertionError', str(cm.output))
            self.assertIn('handle_exception got AssertionError error for function', str(cm.output))

        with self.assertLogs() as cm:
            resp_json = self.raise_exception(StatusCodeException(HTTPStatus.NOT_FOUND))
            self.assertEqual(resp_json.status_code, 404)
            self.assertEqual(resp_json.status, "404 NOT FOUND")
            resp_msg_data = json.loads(resp_json.data.decode('utf-8'))
            self.assertIsInstance(resp_msg_data, dict)
            self.assertEqual(resp_msg_data['message'], 'Not Found')
            self.assertIn('StatusCodeException', str(cm.output))
            self.assertIn('handle_exception got StatusCodeException error for function', str(cm.output))

        with self.assertLogs() as cm:
            resp_json = self.raise_assertion()
            self.assertEqual(resp_json.status_code, 500)
            self.assertEqual(resp_json.status, "500 INTERNAL SERVER ERROR")
            resp_msg_data = json.loads(resp_json.data.decode('utf-8'))
            self.assertIsInstance(resp_msg_data, dict)
            self.assertEqual(resp_msg_data['error'], 'Internal Server Error')
            self.assertIn('AssertionError', str(cm.output))
            self.assertIn('handle_exception got AssertionError error for function', str(cm.output))

    @HandleException()
    def raise_exception(self, excp_type):
        raise excp_type

    @HandleException()
    def raise_assertion(self):
        assert True is False
