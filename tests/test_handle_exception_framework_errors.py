"""@HandleException answers the web framework's own HTTP errors with their status, not with a 500."""
import json
import unittest
from http import HTTPStatus

from flask import Flask, abort

from core_lib.web_helpers.decorators import HandleException
from core_lib.web_helpers.web_helpers_utils import WebHelpersUtils


class TestHandleExceptionFrameworkErrors(unittest.TestCase):

    def setUp(self):
        self._server_type = WebHelpersUtils.server_type

    def tearDown(self):
        WebHelpersUtils.server_type = self._server_type

    def test_flask_abort_keeps_its_status(self):
        WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)
        app = Flask('acme')

        @app.get('/widgets/<int:status>')
        @HandleException()
        def get_widget(status):
            abort(status)

        client = app.test_client()
        for status in (HTTPStatus.NOT_FOUND, HTTPStatus.SERVICE_UNAVAILABLE):  # a `message` body and an `error` body
            response = client.get(f'/widgets/{status.value}')
            self.assertEqual(status.value, response.status_code)
            key = 'error' if status >= 500 else 'message'
            self.assertEqual({key: status.phrase}, response.get_json())

    def test_django_http_errors_keep_their_status(self):
        # Imported here: at module level the test loader touches Django's lazy settings before they are configured.
        from django.conf import settings
        if not settings.configured:
            settings.configure()
        from django.core.exceptions import BadRequest, PermissionDenied, SuspiciousOperation
        from django.http import Http404
        WebHelpersUtils.init(WebHelpersUtils.ServerType.DJANGO)

        expected = [
            (Http404('no widget'), HTTPStatus.NOT_FOUND),
            (PermissionDenied(), HTTPStatus.FORBIDDEN),
            (BadRequest(), HTTPStatus.BAD_REQUEST),
            (SuspiciousOperation(), HTTPStatus.BAD_REQUEST),
        ]
        for error, status in expected:
            @HandleException()
            def view(request):
                raise error

            response = view(None)
            self.assertEqual(status.value, response.status_code, type(error).__name__)
            self.assertEqual({'message': status.phrase}, json.loads(response.content))
