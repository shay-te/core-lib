"""Tests for FastAPI integration in core_lib/web_helpers."""
import json
import unittest
from unittest.mock import MagicMock

from core_lib.helpers.constants import MediaType
from core_lib.session.security_handler import SecurityHandler
from core_lib.web_helpers.fastapi.require_login import RequireLogin
from core_lib.web_helpers.fastapi.user_auth_middleware import UserAuthMiddleware
from core_lib.web_helpers.request_response_helpers import (
    generate_response,
    generate_response_fastapi,
    request_body_dict,
)
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils


class _FastAPIServerTypeFixture(unittest.TestCase):
    """Switch the global server type to FASTAPI for the duration of the test
    and restore the previous value afterwards (other test files use FLASK /
    DJANGO and share global state)."""

    def setUp(self):
        self._previous_server_type = WebHelpersUtils.server_type
        self._previous_security = SecurityHandler.user_security
        WebHelpersUtils.init(WebHelpersUtils.ServerType.FASTAPI)

    def tearDown(self):
        WebHelpersUtils.server_type = self._previous_server_type
        SecurityHandler.user_security = self._previous_security


# ── ServerType enum ─────────────────────────────────────────────────────


class TestFastapiServerType(unittest.TestCase):
    def test_fastapi_added_to_enum(self):
        self.assertEqual(WebHelpersUtils.ServerType.FASTAPI.value, 'fastapi')


# ── generate_response_fastapi ────────────────────────────────────────


class TestGenerateResponseFastapi(_FastAPIServerTypeFixture):
    def test_routed_via_generate_response(self):
        # generate_response (the dispatcher) routes to the fastapi backend
        # when WebHelpersUtils is initialized to FASTAPI.
        resp = generate_response({'k': 'v'}, 200, MediaType.APPLICATION_JSON)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.body, json.dumps({'k': 'v'}).encode())

    def test_text_html_response(self):
        resp = generate_response_fastapi(b'<h1>hi</h1>', 200, MediaType.TEXT_HTML)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('text/html', resp.headers.get('content-type', ''))
        self.assertEqual(resp.body, b'<h1>hi</h1>')

    def test_default_headers_none(self):
        # Mutable-default protection: headers=None must yield an empty dict.
        resp = generate_response_fastapi(b'd', 200, MediaType.TEXT_HTML)
        self.assertEqual(resp.status_code, 200)

    def test_extra_headers_applied(self):
        resp = generate_response_fastapi(
            b'd', 200, MediaType.TEXT_HTML, headers={'X-Custom': 'yes'}
        )
        self.assertEqual(resp.headers['X-Custom'], 'yes')

    def test_accepts_int_enum_status(self):
        from http import HTTPStatus
        resp = generate_response_fastapi(b'', HTTPStatus.NOT_FOUND, MediaType.TEXT_HTML)
        self.assertEqual(resp.status_code, 404)


# ── request_body_dict for FastAPI ────────────────────────────────────


class TestRequestBodyDictFastapi(_FastAPIServerTypeFixture):
    def test_bytes_body_parsed_as_json(self):
        request = MagicMock()
        request.body = b'{"a": 1}'
        self.assertEqual(request_body_dict(request), {'a': 1})

    def test_non_bytes_body_returns_none(self):
        # Callers haven't pre-read the body — we don't have an event loop
        # here, so just return None rather than raising.
        request = MagicMock()
        request.body = MagicMock()  # not bytes/bytearray
        self.assertIsNone(request_body_dict(request))


# ── UserAuthMiddleware ───────────────────────────────────────────────


class TestUserAuthMiddlewareFastapi(_FastAPIServerTypeFixture):
    def test_attaches_user_to_request_state(self):
        from fastapi import FastAPI, Request
        from fastapi.testclient import TestClient

        # Replace SecurityHandler with a mock that returns a known session
        mock_us = MagicMock()
        mock_us.token_to_session_object.return_value = {'id': 42}
        SecurityHandler.user_security = mock_us

        app = FastAPI()
        app.add_middleware(UserAuthMiddleware, cookie_name='my_cookie')

        @app.get('/who')
        def who(request: Request):
            user = getattr(request.state, 'user', None)
            return {'user': user}

        client = TestClient(app)
        client.cookies.set('my_cookie', 'opaque-token')
        r = client.get('/who')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {'user': {'id': 42}})
        mock_us.token_to_session_object.assert_called_once_with('opaque-token')

    def test_no_cookie_means_no_user_attached(self):
        from fastapi import FastAPI, Request
        from fastapi.testclient import TestClient

        mock_us = MagicMock()
        SecurityHandler.user_security = mock_us

        app = FastAPI()
        app.add_middleware(UserAuthMiddleware, cookie_name='my_cookie')

        @app.get('/who')
        def who(request: Request):
            return {'has_user': hasattr(request.state, 'user')}

        client = TestClient(app)
        r = client.get('/who')
        self.assertEqual(r.json(), {'has_user': False})
        mock_us.token_to_session_object.assert_not_called()


# ── RequireLogin decorator ───────────────────────────────────────────


class TestRequireLoginFastapi(_FastAPIServerTypeFixture):
    def setUp(self):
        super().setUp()
        # Install a mock SecurityHandler that approves all requests by
        # default (returns None from _secure_entry → "pass").
        mock_us = MagicMock()
        mock_us._secure_entry = MagicMock(return_value=None)
        SecurityHandler.user_security = mock_us

    def test_passes_request_to_view(self):
        captured = {}

        @RequireLogin(policies=[])
        def view(request):
            captured['request'] = request
            from starlette.responses import Response
            return Response(content=b'ok', status_code=200)

        fake_request = MagicMock()
        fake_request.cookies = {}
        result = view(fake_request)
        self.assertEqual(result.status_code, 200)
        self.assertIs(captured['request'], fake_request)

    def test_unauthorized_response_short_circuits_view(self):
        # _secure_entry returns a truthy response → view is NOT called
        from starlette.responses import Response
        unauthorized = Response(content=b'no', status_code=401)
        SecurityHandler.user_security._secure_entry = MagicMock(
            return_value=unauthorized
        )

        view_calls = []

        @RequireLogin(policies=[])
        def view(request):
            view_calls.append(1)

        result = view(MagicMock())
        self.assertIs(result, unauthorized)
        self.assertEqual(view_calls, [])

    def test_view_exception_yields_500(self):
        # Bug 16 regression for the FastAPI path — view exceptions become
        # proper 500 responses, not None.
        from starlette.responses import Response

        @RequireLogin(policies=[])
        def view(request):
            raise RuntimeError('boom')

        result = view(MagicMock())
        self.assertEqual(result.status_code, 500)

    def test_default_policies_empty(self):
        rl = RequireLogin()
        self.assertEqual(rl.policies, [])


# ── _secure_entry FastAPI cookie branch ─────────────────────────────


class TestSecureEntryFastapi(_FastAPIServerTypeFixture):
    def test_token_extracted_from_request_cookies(self):
        from core_lib.session.user_security import UserSecurity
        from core_lib.session.token_handler import TokenHandler

        captured = {}

        class TH(TokenHandler):
            def encode(self, m): return ''
            def decode(self, e):
                return {'sub': e}

        class US(UserSecurity):
            def secure_entry(self, request, session_obj, policies):
                captured['session_obj'] = session_obj
                return 'ok'
            def from_session_data(self, session_data):
                return {'from': session_data}
            def generate_session_data(self, obj):
                return obj

        us = US('my_cookie', TH())
        request = MagicMock()
        request.cookies = {'my_cookie': 'tok-value'}
        result = us._secure_entry(request, [])
        self.assertEqual(result, 'ok')
        self.assertEqual(captured['session_obj'], {'from': {'sub': 'tok-value'}})


# ── _get_request returns None on FastAPI ────────────────────────────


class TestGetRequestFastapi(_FastAPIServerTypeFixture):
    def test_returns_none(self):
        # FastAPI binds the request per-async-task; there's no thread-local
        # proxy. _get_request returns None and callers attach the request
        # via the error middleware context instead.
        from core_lib.web_helpers.decorators import _get_request
        self.assertIsNone(_get_request())
