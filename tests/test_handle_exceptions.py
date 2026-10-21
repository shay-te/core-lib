import json
import unittest
from http import HTTPStatus

from django.conf import settings
from flask import Flask

from core_lib.core_lib import CoreLib
from core_lib.error_handling.status_code_exception import StatusCodeException
from core_lib.middleware.middleware import Middleware
from core_lib.web_helpers.decorators import HandleException, handle_exception
from core_lib.web_helpers.web_helpers_utils import WebHelpersUtils

if not settings.configured:
    settings.configure()
    settings.DEFAULT_CHARSET = 'utf-8'


class RecordingMiddleware(Middleware):
    # Keeps what each failure looked like. The request is read while it is still the current one.
    def __init__(self):
        self.seen = []

    def handle(self, context) -> None:
        request = context['request']
        self.seen.append({
            'exc': context['exc'],
            'func': context['func'],
            'request_path': None if request is None else request.path,
            'stacktrace': context['stacktrace'],
        })


class FailingMiddleware(Middleware):
    def handle(self, context) -> None:
        raise RuntimeError('acme error reporter is down')


def find_widget(widget_id: int):
    raise StatusCodeException(HTTPStatus.NOT_FOUND, f'no widget {widget_id}')


class TestHandleException(unittest.TestCase):
    def setUp(self):
        self._server_type = WebHelpersUtils.server_type
        self._middlewares = []

    def tearDown(self):
        WebHelpersUtils.server_type = self._server_type
        for middleware in self._middlewares:
            CoreLib.handle_exception_middleware.remove(middleware)

    def _add_middleware(self, middleware: Middleware) -> Middleware:
        # CoreLib.handle_exception_middleware is one chain for the whole process: tearDown takes these out again.
        self._middlewares.append(middleware)
        CoreLib.handle_exception_middleware.add(middleware)
        return middleware

    def test_middleware_gets_the_failure_and_the_flask_request(self):
        WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)
        recorder = self._add_middleware(RecordingMiddleware())
        app = Flask('acme')

        @app.get('/widgets/<int:widget_id>')
        @HandleException()
        def get_widget(widget_id):
            find_widget(widget_id)

        with self.assertLogs('core_lib.web_helpers.decorators', level='ERROR'):
            response = app.test_client().get('/widgets/7')

        self.assertEqual(404, response.status_code)
        self.assertEqual({'message': 'Not Found'}, response.get_json())
        self.assertEqual(1, len(recorder.seen))
        failure = recorder.seen[0]
        self.assertIsInstance(failure['exc'], StatusCodeException)
        self.assertEqual(HTTPStatus.NOT_FOUND, failure['exc'].status_code)
        self.assertIs(get_widget.__wrapped__, failure['func'])
        self.assertEqual('/widgets/7', failure['request_path'])
        self.assertTrue(failure['stacktrace'].startswith('Traceback (most recent call last):'))
        self.assertIn('no widget 7', failure['stacktrace'])

    def test_middleware_gets_no_request_on_django(self):
        from django.test import RequestFactory
        WebHelpersUtils.init(WebHelpersUtils.ServerType.DJANGO)
        recorder = self._add_middleware(RecordingMiddleware())

        @HandleException(log_exception=False)
        def get_widget(request):
            raise RuntimeError('widget store is down')

        with self.assertLogs('core_lib.web_helpers.decorators', level='ERROR'):
            response = get_widget(RequestFactory().get('/widgets/7'))

        self.assertEqual(500, response.status_code)
        self.assertEqual(1, len(recorder.seen))
        self.assertIsNone(recorder.seen[0]['request_path'])
        self.assertEqual('widget store is down', str(recorder.seen[0]['exc']))

    def test_failing_middleware_is_logged_and_the_client_still_gets_its_response(self):
        WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)
        self._add_middleware(FailingMiddleware())
        recorder = self._add_middleware(RecordingMiddleware())

        with self.assertLogs('core_lib.web_helpers.decorators', level='WARNING') as logs:
            response = handle_exception(find_widget, 7)

        self.assertEqual(404, response.status_code)
        self.assertEqual({'message': 'Not Found'}, response.get_json())
        self.assertEqual([], recorder.seen)   # the chain stops at the failing middleware
        warnings = [record.getMessage() for record in logs.records if record.levelname == 'WARNING']
        self.assertEqual(['Error while executing error middlewares: acme error reporter is down'], warnings)

    def test_without_init_a_failure_escapes_as_value_error(self):
        WebHelpersUtils.server_type = None   # an app that never called init()
        recorder = self._add_middleware(RecordingMiddleware())

        @HandleException()
        def list_widgets():
            return ['acme']

        @HandleException()
        def get_widget():
            find_widget(7)

        self.assertEqual(['acme'], list_widgets())   # a function that does not raise works either way
        with self.assertLogs('core_lib.web_helpers.decorators', level='ERROR'):
            with self.assertRaises(ValueError) as context:
                get_widget()

        self.assertEqual('WebHelpersUtils never initialized', str(context.exception))
        self.assertIsInstance(context.exception.__context__, StatusCodeException)
        self.assertEqual(1, len(recorder.seen))   # error hooks still ran, with no request
        self.assertIsNone(recorder.seen[0]['request_path'])

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
