"""The one `RequireLogin`: the old per-framework paths still work, and a Django error report carries its request."""
import importlib
import sys
import unittest
from datetime import timedelta

from django.conf import settings
from django.http import HttpRequest
from flask import Flask

from core_lib.core_lib import CoreLib
from core_lib.middleware.middleware import Middleware
from core_lib.session.jwt_token_handler import JWTTokenHandler
from core_lib.session.security_handler import SecurityHandler
from core_lib.session.user_security import UserSecurity
from core_lib.web_helpers.require_login import RequireLogin
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

    def test_django_error_middleware_gets_the_request(self):
        WebHelpersUtils.init(WebHelpersUtils.ServerType.DJANGO)
        recorder = _RequestRecorder()
        CoreLib.handle_exception_middleware.add(recorder)
        self.addCleanup(CoreLib.handle_exception_middleware.remove, recorder)

        @RequireLogin()
        def view(request):
            raise RuntimeError('boom')

        request = HttpRequest()
        view(request)
        self.assertEqual([request], recorder.requests)
