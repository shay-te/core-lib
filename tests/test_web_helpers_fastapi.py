"""FastAPI support in core_lib/web_helpers, driven through a REAL FastAPI app.

Every request goes through FastAPI routing, Starlette's `Request`, a real cookie, a real JWT and a real
`UserSecurity`. Nothing is mocked: a fake request only proves what the fake allows, and the fakes this file
replaced passed while an async view crashed on every denial and `request_body_dict` always returned None.
"""
import time
import unittest
from datetime import timedelta
from http import HTTPStatus

import jwt
from fastapi import Depends, FastAPI, Request
from fastapi.testclient import TestClient

from core_lib.core_lib import CoreLib
from core_lib.error_handling.status_code_exception import StatusCodeException
from core_lib.helpers.constants import MediaType
from core_lib.middleware.middleware import Middleware
from core_lib.session.jwt_token_handler import JWTTokenHandler
from core_lib.session.security_handler import SecurityHandler
from core_lib.session.user_security import UserSecurity
from core_lib.web_helpers.decorators import _get_request
from core_lib.web_helpers.fastapi.user_auth_middleware import UserAuthMiddleware
from core_lib.web_helpers.request_response_helpers import generate_response, request_body_dict, response_status
from core_lib.web_helpers.require_login import RequireLogin
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils

SECRET = 'fastapi-test-secret'
COOKIE_NAME = 'widget_session'
ROLE_ADMIN = 1
ROLE_REVIEWER = 2
USER_ID = 7
NAMED_HANDLER = 'partner_portal'
NAMED_COOKIE = 'partner_session'


class _RoleSecurity(UserSecurity):
    """Allows a request by returning None, denies it by returning a response — the `secure_entry` contract."""

    def __init__(self, cookie_name=COOKIE_NAME):
        UserSecurity.__init__(self, cookie_name, JWTTokenHandler(SECRET, timedelta(seconds=60)))

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


class _RequestRecorder(Middleware):
    """An error middleware that keeps the request each failure reports."""

    def __init__(self):
        self.requests = []

    def handle(self, context):
        self.requests.append(context['request'])


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

        @app.get('/sync-request-last/{item_id}')
        @RequireLogin()
        def sync_request_last(item_id: int, request: Request):
            return {'item_id': item_id, 'user': request.state.user}

        @app.get('/sync-log-exception')
        @RequireLogin()
        def sync_log_exception(request: Request, log_exception: bool = False):
            return {'log_exception': log_exception}

        @app.get('/named-handler')
        @RequireLogin([ROLE_ADMIN], security_handler_name=NAMED_HANDLER)
        def named_handler(request: Request):
            return {'ok': True}

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
        SecurityHandler.register(_RoleSecurity(NAMED_COOKIE), NAMED_HANDLER)
        self.view_calls.clear()

    def tearDown(self):
        WebHelpersUtils.server_type = self._previous_server_type
        SecurityHandler.user_security = self._previous_security
        SecurityHandler.named_user_securities.pop(NAMED_HANDLER, None)

    def _client(self, token=None, cookie_name=COOKIE_NAME):
        client = TestClient(self.app)
        if token:
            client.cookies.set(cookie_name, token)
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
        self.assertEqual(HTTPStatus.UNAUTHORIZED, response.status_code)
        self.assertEqual([], self.view_calls)

    def test_sync_view_status_code_exception_becomes_that_status(self):
        response = self._client(_token(ROLE_REVIEWER)).get(f'/sync-raises/{HTTPStatus.NOT_FOUND.value}')
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
        self.assertEqual({'message': 'Not Found'}, response.json())

    def test_sync_view_unexpected_error_becomes_500(self):
        response = self._client(_token(ROLE_REVIEWER)).get(f'/sync-raises/{HTTPStatus.INTERNAL_SERVER_ERROR.value}')
        self.assertEqual(HTTPStatus.INTERNAL_SERVER_ERROR, response.status_code)
        self.assertEqual({'error': 'Internal Server Error'}, response.json())

    def test_request_need_not_be_the_first_parameter(self):
        # FastAPI calls a view by keyword, so the view may declare `request` anywhere.
        response = self._client(_token(ROLE_ADMIN)).get('/sync-request-last/3')
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual({'item_id': 3, 'user': {'id': USER_ID, 'role': ROLE_ADMIN}}, response.json())

    def test_view_parameter_named_log_exception_reaches_the_view(self):
        # `handle_exception` has an option of that name. The view's own parameter must not be taken for it.
        response = self._client(_token(ROLE_ADMIN)).get('/sync-log-exception', params={'log_exception': 'true'})
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual({'log_exception': True}, response.json())

    def test_route_runs_the_security_handler_it_names(self):
        # The named handler reads its own cookie, so the default handler's cookie alone must be refused.
        allowed = self._client(_token(ROLE_ADMIN), cookie_name=NAMED_COOKIE).get('/named-handler')
        self.assertEqual(HTTPStatus.OK, allowed.status_code)
        refused = self._client(_token(ROLE_ADMIN)).get('/named-handler')
        self.assertEqual(HTTPStatus.UNAUTHORIZED, refused.status_code)

    def test_async_view_is_refused(self):
        # Views are plain `def`: an `async def` view would hold the event loop through every sync core-lib call.
        async def async_view(request):
            return None

        decorator = RequireLogin()
        with self.assertRaisesRegex(TypeError, 'not `async def`'):
            decorator(async_view)

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

    def test_request_body_dict_in_async_view_says_to_await_request_json(self):
        # An async view runs on the event loop, where a sync helper cannot read the body. It must fail, not
        # return None as if the client had sent nothing, and say what to do instead.
        client = self._client()
        with self.assertRaisesRegex(RuntimeError, r'await request\.json\(\)'):
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

    def test_error_middleware_gets_the_failing_request(self):
        recorder = _RequestRecorder()
        CoreLib.handle_exception_middleware.add(recorder)
        self.addCleanup(CoreLib.handle_exception_middleware.remove, recorder)
        path = f'/sync-raises/{HTTPStatus.INTERNAL_SERVER_ERROR.value}'
        self._client(_token(ROLE_REVIEWER)).get(path)
        self.assertEqual([path], [request and request.url.path for request in recorder.requests])

    def test_request_is_unbound_once_the_view_returns(self):
        # Called directly, in this thread: the wrapper must not leave its request behind for a later error report.
        request = Request({'type': 'http', 'method': 'GET', 'path': '/', 'query_string': b'',
                           'headers': [(b'cookie', f'{COOKIE_NAME}={_token(ROLE_ADMIN)}'.encode())]})
        RequireLogin()(lambda request: None)(request=request)
        self.assertIsNone(_get_request())

    def test_get_request_returns_none(self):
        # Only a `@RequireLogin` view binds the request, and only while it runs.
        self.assertIsNone(_get_request())
