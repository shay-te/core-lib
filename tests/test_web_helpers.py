import json
import unittest
from http import HTTPStatus

from django.conf import settings

from core_lib.web_helpers.request_response_helpers import response_status, response_ok, response_message, response_json
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils

if not settings.configured:
    settings.configure()
    settings.DEFAULT_CHARSET = 'utf-8'


class TestWebHelpers(unittest.TestCase):
    def test_web_utils_flask(self):
        web_util = WebHelpersUtils()

        web_util.init(web_util.ServerType.FLASK)
        self.assertEqual(web_util.get_server_type(), web_util.ServerType.FLASK)

        # Response Status
        resp_status = response_status(HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertEqual(resp_status.status_code, 500)
        self.assertEqual(resp_status.status, "500 INTERNAL SERVER ERROR")
        resp_status_data = resp_status.data.decode('utf-8')
        self.assertEqual(resp_status_data, '')

        resp_status = response_status(HTTPStatus.OK)
        self.assertEqual(resp_status.status_code, 200)
        self.assertEqual(resp_status.status, "200 OK")
        resp_status_data = resp_status.data.decode('utf-8')
        self.assertEqual(resp_status_data, '')

        resp_status = response_status(HTTPStatus.NOT_FOUND)
        self.assertEqual(resp_status.status_code, 404)
        self.assertEqual(resp_status.status, "404 NOT FOUND")
        resp_status_data = resp_status.data.decode('utf-8')
        self.assertEqual(resp_status_data, '')

        # Response Ok
        resp_ok = response_ok()
        self.assertEqual(resp_ok.status_code, 200)
        self.assertEqual(resp_ok.status, "200 OK")
        resp_ok_data = json.loads(resp_ok.data.decode('utf-8'))
        self.assertIsInstance(resp_ok_data, dict)
        self.assertEqual(resp_ok_data['message'], 'ok')

        # Response Message
        resp_msg = response_message('hello world', HTTPStatus.OK)
        self.assertEqual(resp_msg.status_code, 200)
        self.assertEqual(resp_msg.status, "200 OK")
        resp_msg_data = json.loads(resp_msg.data.decode('utf-8'))
        self.assertIsInstance(resp_msg_data, dict)
        self.assertEqual(resp_msg_data['message'], 'hello world')

        resp_msg = response_message('some error occurred', HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertEqual(resp_msg.status_code, 500)
        self.assertEqual(resp_msg.status, "500 INTERNAL SERVER ERROR")
        resp_msg_data = json.loads(resp_msg.data.decode('utf-8'))
        self.assertIsInstance(resp_msg_data, dict)
        self.assertEqual(resp_msg_data['error'], 'some error occurred')

        resp_msg = response_message('Not Found', HTTPStatus.NOT_FOUND)
        self.assertEqual(resp_msg.status_code, 404)
        self.assertEqual(resp_msg.status, "404 NOT FOUND")
        resp_msg_data = json.loads(resp_msg.data.decode('utf-8'))
        self.assertIsInstance(resp_msg_data, dict)
        self.assertEqual(resp_msg_data['message'], 'Not Found')

        # Response JSON
        resp_json = response_json({'username': 'Jon Doe'}, HTTPStatus.OK)
        self.assertEqual(resp_json.status_code, 200)
        self.assertEqual(resp_json.status, "200 OK")
        resp_json_data = json.loads(resp_json.data.decode('utf-8'))
        self.assertIsInstance(resp_json_data, dict)
        self.assertEqual(resp_json_data['username'], 'Jon Doe')

        resp_json = response_json({'error': 'Server Error'}, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertEqual(resp_json.status_code, 500)
        self.assertEqual(resp_json.status, "500 INTERNAL SERVER ERROR")
        resp_json_data = json.loads(resp_json.data.decode('utf-8'))
        self.assertIsInstance(resp_json_data, dict)
        self.assertEqual(resp_json_data['error'], 'Server Error')

        resp_json = response_json({'error': 'file not found'}, HTTPStatus.NOT_FOUND)
        self.assertEqual(resp_json.status_code, 404)
        self.assertEqual(resp_json.status, "404 NOT FOUND")
        resp_json_data = json.loads(resp_json.data.decode('utf-8'))
        self.assertIsInstance(resp_json_data, dict)
        self.assertEqual(resp_json_data['error'], 'file not found')

    def test_web_utils_django(self):
        web_util = WebHelpersUtils()

        web_util.init(web_util.ServerType.DJANGO)
        self.assertEqual(web_util.get_server_type(), web_util.ServerType.DJANGO)

        # Response Status
        resp_status = response_status(HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertEqual(resp_status.status_code, 500)
        resp_status_data = resp_status.content.decode('utf-8')
        self.assertEqual(resp_status_data, '')

        resp_status = response_status(HTTPStatus.OK)
        self.assertEqual(resp_status.status_code, 200)
        resp_status_data = resp_status.content.decode('utf-8')
        self.assertEqual(resp_status_data, '')

        resp_status = response_status(HTTPStatus.NOT_FOUND)
        self.assertEqual(resp_status.status_code, 404)
        resp_status_data = resp_status.content.decode('utf-8')
        self.assertEqual(resp_status_data, '')

        # Response Ok
        resp_ok = response_ok()
        self.assertEqual(resp_ok.status_code, 200)
        resp_ok_data = json.loads(resp_ok.content.decode('utf-8'))
        self.assertIsInstance(resp_ok_data, dict)
        self.assertEqual(resp_ok_data['message'], 'ok')

        # Response Message
        resp_msg = response_message('hello world', HTTPStatus.OK)
        self.assertEqual(resp_msg.status_code, 200)
        resp_msg_data = json.loads(resp_msg.content.decode('utf-8'))
        self.assertIsInstance(resp_msg_data, dict)
        self.assertEqual(resp_msg_data['message'], 'hello world')

        resp_msg = response_message('some error occurred', HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertEqual(resp_msg.status_code, 500)
        resp_msg_data = json.loads(resp_msg.content.decode('utf-8'))
        self.assertIsInstance(resp_msg_data, dict)
        self.assertEqual(resp_msg_data['error'], 'some error occurred')

        resp_msg = response_message('Not Found', HTTPStatus.NOT_FOUND)
        self.assertEqual(resp_msg.status_code, 404)
        resp_msg_data = json.loads(resp_msg.content.decode('utf-8'))
        self.assertIsInstance(resp_msg_data, dict)
        self.assertEqual(resp_msg_data['message'], 'Not Found')

        # Response JSON
        resp_json = response_json({'username': 'Jon Doe'}, HTTPStatus.OK)
        self.assertEqual(resp_json.status_code, 200)
        resp_json_data = json.loads(resp_json.content.decode('utf-8'))
        self.assertIsInstance(resp_json_data, dict)
        self.assertEqual(resp_json_data['username'], 'Jon Doe')

        resp_json = response_json({'error': 'Server Error'}, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertEqual(resp_json.status_code, 500)
        resp_json_data = json.loads(resp_json.content.decode('utf-8'))
        self.assertIsInstance(resp_json_data, dict)
        self.assertEqual(resp_json_data['error'], 'Server Error')

        resp_json = response_json({'error': 'file not found'}, HTTPStatus.NOT_FOUND)
        self.assertEqual(resp_json.status_code, 404)
        resp_json_data = json.loads(resp_json.content.decode('utf-8'))
        self.assertIsInstance(resp_json_data, dict)
        self.assertEqual(resp_json_data['error'], 'file not found')
