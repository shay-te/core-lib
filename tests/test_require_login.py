"""The one `RequireLogin`: the old per-framework paths still work, and a Django error report carries its request."""
import importlib
import sys
import threading
import unittest
from datetime import timedelta

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpRequest, HttpResponse
from django.test import Client, override_settings
from django.urls import path
from flask import Flask

from core_lib.core_lib import CoreLib
from core_lib.middleware.middleware import Middleware
from core_lib.session.jwt_token_handler import JWTTokenHandler
from core_lib.session.security_handler import SecurityHandler
from core_lib.session.user_security import UserSecurity
from core_lib.web_helpers.decorators import HandleException, _get_request
from core_lib.web_helpers.require_login import RequireLogin
from core_lib.web_helpers.require_login_helper import require_login
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils

DEPRECATED_PATHS = ('core_lib.web_helpers.flask.require_login', 'core_lib.web_helpers.django.require_login')


class _AllowEveryone(UserSecurity):
    def __init__(self):
        UserSecurity.__init__(self, 'session', JWTTokenHandler('secret', timedelta(seconds=60)))

    def secure_entry(self, request, session_obj, policies):
        return None

    def from_session_data(self, session_data):
        return session_data

    def generate_session_data(self, obj):
        return obj


class _RequestRecorder(Middleware):
    """An error middleware that keeps the request each failure reports."""

    def __init__(self):
        self.requests = []

    def handle(self, context):
        self.requests.append(context['request'])


# Views a real Django routes to (ROOT_URLCONF is this module). Each keeps the request Django built, so a test can
# compare it BY IDENTITY with what `_get_request()` returned and with what an error middleware received.
_views_saw = {}
_both_inside = threading.Barrier(2, timeout=5)


@RequireLogin()
def _reads_its_request(request):
    _views_saw[request.path] = (request, _get_request())
    return HttpResponse()


@RequireLogin()
def _raises(request):
    _views_saw[request.path] = request
    raise RuntimeError('boom')


@RequireLogin()
@HandleException()
def _raises_under_handle_exception(request):
    _views_saw[request.path] = request
    raise RuntimeError('boom')


@RequireLogin()
def _reads_its_request_while_another_runs(request, name):
    _both_inside.wait()  # both requests are bound before either one reads
    _views_saw[request.path] = (request, _get_request())
    _both_inside.wait()  # and neither is released before both have read
    return HttpResponse()


urlpatterns = [
    path('reads', _reads_its_request),
    path('raises', _raises),
    path('raises-handled', _raises_under_handle_exception),
    path('together/<str:name>', _reads_its_request_while_another_runs),
]


class TestRequireLogin(unittest.TestCase):

    def setUp(self):
        if not settings.configured:
            settings.configure()
        self.addCleanup(setattr, WebHelpersUtils, 'server_type', WebHelpersUtils.server_type)
        self.addCleanup(setattr, SecurityHandler, 'user_security', SecurityHandler.user_security)
        SecurityHandler.user_security = _AllowEveryone()

    def test_django_view_gets_its_request_and_url_arguments(self):
        WebHelpersUtils.init(WebHelpersUtils.ServerType.DJANGO)

        @RequireLogin()
        def view(request, item_id, page):
            return request, item_id, page

        request = HttpRequest()
        self.assertEqual((request, 5, 2), view(request, 5, page=2))

    def test_flask_view_gets_its_url_arguments(self):
        WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)

        @RequireLogin()
        def view(item_id, page):
            return item_id, page

        with Flask(__name__).test_request_context():
            self.assertEqual((5, 2), view(5, page=2))

    def test_old_paths_give_the_same_decorator_and_warn(self):
        for module_name in DEPRECATED_PATHS:
            with self.subTest(module=module_name):
                sys.modules.pop(module_name, None)
                with self.assertWarnsRegex(DeprecationWarning, r'core_lib\.web_helpers\.require_login'):
                    module = importlib.import_module(module_name)
                self.assertIs(RequireLogin, module.RequireLogin)

    # Through a real Django: Django builds the request and routes to the view. master's `_get_request` returned
    # None for Django, even inside a view, so an error middleware never learned which request failed.

    def _django_client(self):
        WebHelpersUtils.init(WebHelpersUtils.ServerType.DJANGO)
        _views_saw.clear()
        routed_here = override_settings(ROOT_URLCONF=__name__, ALLOWED_HOSTS=['testserver'])
        routed_here.enable()
        self.addCleanup(routed_here.disable)
        return Client(raise_request_exception=False)

    def _record_errors(self):
        recorder = _RequestRecorder()
        CoreLib.handle_exception_middleware.add(recorder)
        self.addCleanup(CoreLib.handle_exception_middleware.remove, recorder)
        return recorder

    def test_django_view_gets_the_request_django_built_from_get_request(self):
        response = self._django_client().get('/reads')
        self.assertEqual(200, response.status_code)
        request, got = _views_saw['/reads']
        self.assertIsInstance(request, WSGIRequest)
        self.assertIs(request, got)

    def test_django_error_middleware_gets_the_request_django_built(self):
        client = self._django_client()
        recorder = self._record_errors()
        for url in ('/raises', '/raises-handled'):
            with self.subTest(url=url):
                recorder.requests.clear()
                self.assertEqual(500, client.get(url).status_code)
                self.assertEqual(1, len(recorder.requests))
                self.assertIs(_views_saw[url], recorder.requests[0])

    def test_django_request_is_released_after_the_response(self):
        self.assertEqual(200, self._django_client().get('/reads').status_code)
        self.assertIsNone(_get_request())

    def test_concurrent_django_requests_each_get_their_own(self):
        # Django serves requests on several threads at once. With one module-level variable instead of the
        # ContextVar, both views would read whichever request was bound last.
        self._django_client()
        statuses = []

        def get(name):
            statuses.append(Client(raise_request_exception=False).get(f'/together/{name}').status_code)

        threads = [threading.Thread(target=get, args=(name,)) for name in ('first', 'second')]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(10)
        self.assertEqual([200, 200], statuses)
        for name in ('first', 'second'):
            with self.subTest(name=name):
                request, got = _views_saw[f'/together/{name}']
                self.assertEqual(f'/together/{name}', request.path)
                self.assertIs(request, got)

    # `require_login` is the whole implementation: called without the decorator, it behaves the same.

    def test_direct_call_reports_the_request_to_error_middlewares(self):
        WebHelpersUtils.init(WebHelpersUtils.ServerType.DJANGO)
        recorder = _RequestRecorder()
        CoreLib.handle_exception_middleware.add(recorder)
        self.addCleanup(CoreLib.handle_exception_middleware.remove, recorder)

        def view(request):
            raise RuntimeError('boom')

        request = HttpRequest()
        require_login([], view, request)
        self.assertEqual([request], recorder.requests)

    def test_direct_call_refuses_an_async_view(self):
        async def view(request):
            return None

        request = HttpRequest()
        with self.assertRaisesRegex(TypeError, 'not `async def`'):
            require_login([], view, request)
