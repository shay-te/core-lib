import json
import unittest
from http import HTTPStatus

from django.conf import settings
from flask import Flask, request as flask_request

from core_lib.helpers.constants import MediaType
from core_lib.web_helpers.decorators import HandleException
from core_lib.web_helpers.request_response_helpers import (
    request_body_dict,
    response_download_content,
    response_error,
    response_json,
    response_message,
    response_ok,
    response_status,
)
from core_lib.web_helpers.web_helpers_utils import WebHelpersUtils

if not settings.configured:
    settings.configure()
    settings.DEFAULT_CHARSET = 'utf-8'


class TestWebHelpers(unittest.TestCase):
    def setUp(self):
        self._server_type = WebHelpersUtils.server_type

    def tearDown(self):
        WebHelpersUtils.server_type = self._server_type

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

        resp_json = response_json({})
        resp_json_data = json.loads(resp_json.data.decode('utf-8'))
        self.assertIsInstance(resp_json_data, dict)
        self.assertEqual(resp_json_data, {})

        resp_json = response_json([])
        resp_json_data = json.loads(resp_json.data.decode('utf-8'))
        self.assertIsInstance(resp_json_data, list)
        self.assertEqual(resp_json_data, [])

        resp_json = response_json(None)
        resp_json_data = resp_json.data.decode('utf-8')
        self.assertIsInstance(resp_json_data, str)
        self.assertEqual(resp_json_data, '')

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

        resp_json = response_json({})
        resp_json_data = json.loads(resp_json.content.decode('utf-8'))
        self.assertIsInstance(resp_json_data, dict)
        self.assertEqual(resp_json_data, {})

        resp_json = response_json([])
        resp_json_data = json.loads(resp_json.content.decode('utf-8'))
        self.assertIsInstance(resp_json_data, list)
        self.assertEqual(resp_json_data, [])

        resp_json = response_json(None)
        resp_json_data = resp_json.content.decode('utf-8')
        self.assertIsInstance(resp_json_data, str)
        self.assertEqual(resp_json_data, '')

    def test_helpers_need_init(self):
        WebHelpersUtils.server_type = None   # an app that never called init()

        with self.assertRaises(ValueError) as context:
            WebHelpersUtils.get_server_type()
        self.assertEqual('WebHelpersUtils never initialized', str(context.exception))
        with self.assertRaises(ValueError):
            response_ok()

    def test_init_refuses_anything_but_a_server_type(self):
        # A plain 'flask' used to be accepted, and then every helper silently returned None.
        WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)
        for server_type in ('flask', None):
            with self.assertRaises(ValueError) as context:
                WebHelpersUtils.init(server_type)
            self.assertEqual(
                f'server_type must be a WebHelpersUtils.ServerType, got `{server_type!r}`', str(context.exception)
            )
        self.assertIs(WebHelpersUtils.ServerType.FLASK, WebHelpersUtils.get_server_type())  # unchanged

    def test_response_error_flask(self):
        WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)

        expected = [
            (response_error(), 500, {'error': 'Internal Server Error'}),
            (response_error('widget store is down'), 500, {'error': 'widget store is down'}),
            (response_error(status=HTTPStatus.BAD_REQUEST), 400, {'error': 'Bad Request'}),   # always `error`
            (response_error('no widget', HTTPStatus.NOT_FOUND), 404, {'error': 'no widget'}),
            (response_error(status=599), 599, {'error': ''}),   # no standard reason phrase
        ]
        for response, status, body in expected:
            self.assertEqual(status, response.status_code)
            self.assertEqual('application/json', response.content_type)
            self.assertEqual(body, json.loads(response.data.decode('utf-8')))

    def test_response_error_django(self):
        WebHelpersUtils.init(WebHelpersUtils.ServerType.DJANGO)

        expected = [
            (response_error(), 500, {'error': 'Internal Server Error'}),
            (response_error(status=HTTPStatus.BAD_REQUEST), 400, {'error': 'Bad Request'}),
        ]
        for response, status, body in expected:
            self.assertEqual(status, response.status_code)
            self.assertEqual('application/json', response['Content-Type'])
            self.assertEqual(body, json.loads(response.content.decode('utf-8')))

    def test_response_download_content_flask(self):
        WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)

        csv_response = response_download_content(b'id,name\n1,acme\n', MediaType.TEXT_PLAIN, 'widgets.csv')
        pdf_response = response_download_content(b'%PDF-1.4 acme', MediaType.APPLICATION_PDF, 'widget report.pdf')

        self.assertEqual(200, csv_response.status_code)
        self.assertEqual('text/plain; charset=utf-8', csv_response.headers['Content-Type'])
        self.assertEqual('attachment; filename="widgets.csv"', csv_response.headers['Content-Disposition'])
        self.assertEqual(b'id,name\n1,acme\n', csv_response.data)
        self.assertEqual('application/pdf', pdf_response.headers['Content-Type'])
        self.assertEqual('attachment; filename="widget report.pdf"', pdf_response.headers['Content-Disposition'])
        self.assertEqual(b'%PDF-1.4 acme', pdf_response.data)

    def test_response_download_content_django(self):
        WebHelpersUtils.init(WebHelpersUtils.ServerType.DJANGO)

        response = response_download_content('id,name\n1,acme\n', MediaType.TEXT_PLAIN, 'widgets.csv')

        self.assertEqual(200, response.status_code)
        self.assertEqual('text/plain', response['Content-Type'])
        self.assertEqual('attachment; filename="widgets.csv"', response['Content-Disposition'])
        self.assertEqual(b'id,name\n1,acme\n', response.content)

    def test_request_body_dict_flask(self):
        WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)
        app = Flask('acme')

        with app.test_request_context('/widgets', method='POST', json={'name': 'acme', 'tags': ['new']}):
            self.assertEqual({'name': 'acme', 'tags': ['new']}, request_body_dict(flask_request))
        with app.test_request_context('/widgets', method='POST', json=[1, 2]):
            self.assertEqual([1, 2], request_body_dict(flask_request))

    def test_request_body_dict_flask_errors_keep_flasks_status(self):
        # Flask refuses a body that is not JSON itself (415, or 400 for broken JSON); @HandleException keeps that status.
        WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)
        app = Flask('acme')

        @app.post('/widgets')
        @HandleException()
        def create_widget():
            return response_json(request_body_dict(flask_request), HTTPStatus.CREATED)

        client = app.test_client()
        created = client.post('/widgets', json={'name': 'acme'})
        with self.assertLogs('core_lib.web_helpers.decorators', level='ERROR'):
            form = client.post('/widgets', data={'name': 'acme'})
        with self.assertLogs('core_lib.web_helpers.decorators', level='ERROR'):
            broken = client.post('/widgets', data='{"name": ', content_type='application/json')

        self.assertEqual((201, {'name': 'acme'}), (created.status_code, created.get_json()))
        self.assertEqual((415, {'message': 'Unsupported Media Type'}), (form.status_code, form.get_json()))
        self.assertEqual((400, {'message': 'Bad Request'}), (broken.status_code, broken.get_json()))

    def test_request_body_dict_django(self):
        from django.test import RequestFactory
        WebHelpersUtils.init(WebHelpersUtils.ServerType.DJANGO)

        widget = RequestFactory().post('/widgets', data='{"name": "acme", "tags": ["new"]}', content_type='application/json')
        unicode_widget = RequestFactory().post('/widgets', data='{"name": "café"}', content_type='application/json')
        empty = RequestFactory().post('/widgets', data='', content_type='application/json')

        self.assertEqual({'name': 'acme', 'tags': ['new']}, request_body_dict(widget))
        self.assertEqual({'name': 'café'}, request_body_dict(unicode_widget))
        with self.assertRaises(json.JSONDecodeError):
            request_body_dict(empty)
