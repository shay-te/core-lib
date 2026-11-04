"""FastAPI support in core_lib/web_helpers, driven through a REAL FastAPI app.

Every request goes through FastAPI routing, Starlette's `Request`, a real cookie, a real JWT and a real
`UserSecurity`. Nothing is mocked: a fake request only proves what the fake allows, and the fakes this file
replaced passed while an async view crashed on every denial and `request_body_dict` always returned None.
"""
import inspect
import time
import unittest
from datetime import timedelta
from http import HTTPStatus

import jwt
from fastapi import Depends, FastAPI, Request
from fastapi.testclient import TestClient

from core_lib.error_handling.status_code_exception import StatusCodeException
from core_lib.helpers.constants import MediaType
from core_lib.session.jwt_token_handler import JWTTokenHandler
from core_lib.session.security_handler import SecurityHandler
from core_lib.session.user_security import UserSecurity
from core_lib.web_helpers.decorators import _get_request
from core_lib.web_helpers.fastapi.require_login import RequireLogin
from core_lib.web_helpers.fastapi.user_auth_middleware import UserAuthMiddleware
from core_lib.web_helpers.request_response_helpers import generate_response, request_body_dict, response_status
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils

SECRET = 'fastapi-test-secret'
COOKIE_NAME = 'widget_session'
ROLE_ADMIN = 1
ROLE_REVIEWER = 2
USER_ID = 7


class _RoleSecurity(UserSecurity):
    """Allows a request by returning None, denies it by returning a response — the `secure_entry` contract."""

    def __init__(self):
        UserSecurity.__init__(self, COOKIE_NAME, JWTTokenHandler(SECRET, timedelta(seconds=60)))

    def secure_entry(self, request, session_obj, policies):
        if session_obj is None:
            return response_status(HTTPStatus.UNAUTHORIZED)
        if policies and session_obj['role'] not in policies:
            return response_status(HTTPStatus.FORBIDDEN)
        return None

    def from_session_data(self, session_data):
        return {'id': session_data['id'], 'role': session_data['role']}

    def generate_session_data(self, obj):
        return {'id': obj['id'], 'role': obj['role']}


def _token(role, expires_in_seconds=60):
    # Minted with an absolute epoch: `JWTTokenHandler.encode` reads a naive `utcnow()` as local time,
    # so on a machine east of UTC its tokens are born expired.
    return jwt.encode({'id': USER_ID, 'role': role, 'exp': int(time.time()) + expires_in_seconds}, SECRET)


def _page_size(size: int = 10):
    return size


class TestWebHelpersFastapi(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.view_calls = []
        app = FastAPI()
        app.add_middleware(UserAuthMiddleware, cookie_name=COOKIE_NAME)

        @app.get('/sync/{item_id}')
        @RequireLogin([ROLE_ADMIN, ROLE_REVIEWER])
        def sync_item(request: Request, item_id: int, q: str = 'none', size: int = Depends(_page_size)):
            cls.view_calls.append('sync_item')
            return {'item_id': item_id, 'q': q, 'size': size, 'user': request.state.user}

        @app.get('/sync-admin')
        @RequireLogin([ROLE_ADMIN])
        def sync_admin(request: Request):
            cls.view_calls.append('sync_admin')
            return {'ok': True}

        @app.get('/sync-raises/{status}')
        @RequireLogin()
        def sync_raises(request: Request, status: int):
            if status == HTTPStatus.INTERNAL_SERVER_ERROR:
                raise RuntimeError('boom')
            raise StatusCodeException(status)

        @app.get('/async/{item_id}')
        @RequireLogin([ROLE_ADMIN, ROLE_REVIEWER])
        async def async_item(request: Request, item_id: int, q: str = 'none'):
            cls.view_calls.append('async_item')
            return {'item_id': item_id, 'q': q, 'user': request.state.user}

        @app.get('/async-admin')
        @RequireLogin([ROLE_ADMIN])
        async def async_admin(request: Request):
            cls.view_calls.append('async_admin')
            return {'ok': True}

        @app.get('/async-raises/{status}')
        @RequireLogin()
        async def async_raises(request: Request, status: int):
            if status == HTTPStatus.INTERNAL_SERVER_ERROR:
                raise RuntimeError('boom')
            raise StatusCodeException(status)

        @app.get('/html')
        @RequireLogin()
        def html(request: Request):
            return generate_response('<h1>widget</h1>', HTTPStatus.CREATED, MediaType.TEXT_HTML, {'X-Widget': 'acme'})

        @app.get('/who')
        def who(request: Request):
            return {'has_user': hasattr(request.state, 'user'), 'user': getattr(request.state, 'user', None)}

        @app.post('/body-sync')
        def body_sync(request: Request):
            return {'parsed': request_body_dict(request)}

        @app.post('/body-async')
        async def body_async(request: Request):
            return {'parsed': request_body_dict(request)}

        cls.app = app

    def setUp(self):
        self._previous_server_type = WebHelpersUtils.server_type
        self._previous_security = SecurityHandler.user_security
        WebHelpersUtils.init(WebHelpersUtils.ServerType.FASTAPI)
        SecurityHandler.user_security = _RoleSecurity()
        self.view_calls.clear()

    def tearDown(self):
        WebHelpersUtils.server_type = self._previous_server_type
        SecurityHandler.user_security = self._previous_security

    def _client(self, token=None):
        client = TestClient(self.app)
        if token:
            client.cookies.set(COOKIE_NAME, token)
        return client

    # RequireLogin, sync views

    def test_sync_view_gets_request_path_query_dependency_and_user(self):
        response = self._client(_token(ROLE_REVIEWER)).get('/sync/5', params={'q': 'acme', 'size': 3})
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual({'item_id': 5, 'q': 'acme', 'size': 3, 'user': {'id': USER_ID, 'role': ROLE_REVIEWER}},
                         response.json())
        self.assertEqual(['sync_item'], self.view_calls)

    def test_sync_view_defaults_reach_the_view(self):
        response = self._client(_token(ROLE_ADMIN)).get('/sync/1')
        self.assertEqual({'item_id': 1, 'q': 'none', 'size': 10, 'user': {'id': USER_ID, 'role': ROLE_ADMIN}},
                         response.json())

    def test_sync_view_without_cookie_is_401_and_view_never_runs(self):
        response = self._client().get('/sync/5')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, response.status_code)
        self.assertEqual([], self.view_calls)

    def test_sync_view_with_wrong_role_is_403_and_view_never_runs(self):
        response = self._client(_token(ROLE_REVIEWER)).get('/sync-admin')
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)
        self.assertEqual([], self.view_calls)

    def test_sync_view_with_expired_token_is_401(self):
        response = self._client(_token(ROLE_ADMIN, expires_in_seconds=-10)).get('/sync/5')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, response.status_code)
        self.assertEqual({'message': 'Unauthorized'}, response.json())
        self.assertEqual([], self.view_calls)

    def test_sync_view_with_token_signed_by_another_secret_never_runs(self):
        forged = jwt.encode({'id': USER_ID, 'role': ROLE_ADMIN, 'exp': int(time.time()) + 60}, 'not-the-secret')
        response = self._client(forged).get('/sync/5')
        # Only the view not running is pinned. The status is 500 today, not 401: `_get_exception_status_code`
        # maps ExpiredSignatureError alone, for every server type.
        self.assertNotEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual([], self.view_calls)

    def test_sync_view_status_code_exception_becomes_that_status(self):
        response = self._client(_token(ROLE_REVIEWER)).get(f'/sync-raises/{HTTPStatus.NOT_FOUND.value}')
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
        self.assertEqual({'message': 'Not Found'}, response.json())

    def test_sync_view_unexpected_error_becomes_500(self):
        response = self._client(_token(ROLE_REVIEWER)).get(f'/sync-raises/{HTTPStatus.INTERNAL_SERVER_ERROR.value}')
        self.assertEqual(HTTPStatus.INTERNAL_SERVER_ERROR, response.status_code)
        self.assertEqual({'error': 'Internal Server Error'}, response.json())

    # RequireLogin, async views

    def test_async_view_allowed_gets_request_path_query_and_user(self):
        response = self._client(_token(ROLE_ADMIN)).get('/async/9', params={'q': 'widget'})
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual({'item_id': 9, 'q': 'widget', 'user': {'id': USER_ID, 'role': ROLE_ADMIN}}, response.json())
        self.assertEqual(['async_item'], self.view_calls)

    def test_async_view_with_wrong_role_is_403_and_view_never_runs(self):
        response = self._client(_token(ROLE_REVIEWER)).get('/async-admin')
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)
        self.assertEqual([], self.view_calls)

    def test_async_view_without_cookie_is_401(self):
        response = self._client().get('/async/9')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, response.status_code)
        self.assertEqual([], self.view_calls)

    def test_async_view_status_code_exception_becomes_that_status(self):
        response = self._client(_token(ROLE_REVIEWER)).get(f'/async-raises/{HTTPStatus.CONFLICT.value}')
        self.assertEqual(HTTPStatus.CONFLICT, response.status_code)
        self.assertEqual({'message': 'Conflict'}, response.json())

    def test_async_view_unexpected_error_becomes_500(self):
        response = self._client(_token(ROLE_REVIEWER)).get(f'/async-raises/{HTTPStatus.INTERNAL_SERVER_ERROR.value}')
        self.assertEqual(HTTPStatus.INTERNAL_SERVER_ERROR, response.status_code)
        self.assertEqual({'error': 'Internal Server Error'}, response.json())

    def test_wrapper_matches_the_view_kind(self):
        # A FastAPI that does not follow `__wrapped__` decides sync/async from the wrapper alone. A sync wrapper
        # around an async view would hand it an un-awaited coroutine, and the current FastAPI hides that.
        async def async_view(request):
            return None

        def sync_view(request):
            return None

        self.assertTrue(inspect.iscoroutinefunction(RequireLogin()(async_view)))
        self.assertFalse(inspect.iscoroutinefunction(RequireLogin()(sync_view)))

    def test_openapi_documents_the_view_parameters_not_the_wrapper(self):
        parameters = self.app.openapi()['paths']['/sync/{item_id}']['get']['parameters']
        self.assertEqual(['item_id', 'q', 'size'], [parameter['name'] for parameter in parameters])

    # generate_response

    def test_generate_response_status_media_type_and_headers(self):
        response = self._client(_token(ROLE_REVIEWER)).get('/html')
        self.assertEqual(HTTPStatus.CREATED, response.status_code)
        self.assertEqual('<h1>widget</h1>', response.text)
        self.assertTrue(response.headers['content-type'].startswith(MediaType.TEXT_HTML.value))
        self.assertEqual('acme', response.headers['X-Widget'])

    # request_body_dict

    def test_request_body_dict_in_sync_view_parses_the_json_body(self):
        body = {'name': 'widget', 'tags': ['a', 'b'], 'owner': {'id': 1}}
        response = self._client().post('/body-sync', json=body)
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual({'parsed': body}, response.json())

    def test_request_body_dict_in_async_view_fails_loudly(self):
        # An async view runs on the event loop, where a sync helper cannot read the body. It must fail, not
        # return None as if the client had sent nothing.
        client = self._client()
        with self.assertRaises(RuntimeError):
            client.post('/body-async', json={'name': 'widget'})

    # UserAuthMiddleware

    def test_middleware_attaches_the_decoded_user(self):
        response = self._client(_token(ROLE_ADMIN)).get('/who')
        self.assertEqual({'has_user': True, 'user': {'id': USER_ID, 'role': ROLE_ADMIN}}, response.json())

    def test_middleware_without_cookie_attaches_nothing(self):
        self.assertEqual({'has_user': False, 'user': None}, self._client().get('/who').json())

    def test_middleware_with_garbage_cookie_attaches_none(self):
        self.assertEqual({'has_user': True, 'user': None}, self._client('not-a-jwt').get('/who').json())

    # _get_request

    def test_get_request_returns_none(self):
        # No thread-local request on FastAPI; error middlewares get the request from their context instead.
        self.assertIsNone(_get_request())
