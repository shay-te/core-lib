"""SecurityHandler keeps named handlers beside the default one, and RequireLogin runs the one a route names."""
import unittest
from datetime import timedelta, datetime

import jwt
from flask import Flask
from werkzeug.http import dump_cookie

from core_lib.data_transform.result_to_dict import result_to_dict
from core_lib.session.security_handler import SecurityHandler
from core_lib.web_helpers.flask.require_login import RequireLogin
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
from tests.test_data.test_user_security_utils import CustomerSecurity, user_data_access, User

SECRET_KEY = 'named-handler-secret'
NAMED_HANDLER = 'named_handler'
NAMED_COOKIE = 'named_cookie'
OTHER_COOKIE = 'other_cookie'


class TestSecurityHandlerNamed(unittest.TestCase):

    def setUp(self):
        WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)
        self.named_security = CustomerSecurity(NAMED_COOKIE, SECRET_KEY, timedelta(seconds=30))
        SecurityHandler.register(self.named_security, NAMED_HANDLER)
        user = result_to_dict(
            user_data_access.create({'username': 'named', 'email': 'named@def.com', 'role': User.PolicyRoles.ADMIN})
        )
        user['exp'] = datetime.now() + timedelta(seconds=30)
        self.token = jwt.encode(user, SECRET_KEY)
        self.app = Flask(__name__)

    def tearDown(self):
        SecurityHandler.named_user_securities.pop(NAMED_HANDLER, None)

    def _call_view(self, cookie_name: str):
        @RequireLogin([User.PolicyRoles.ADMIN], security_handler_name=NAMED_HANDLER)
        def view():
            return None

        with self.app.test_request_context(environ_base={'HTTP_COOKIE': dump_cookie(cookie_name, self.token)}):
            return view()

    def test_get_returns_named_handler(self):
        self.assertIs(SecurityHandler.get(NAMED_HANDLER), self.named_security)

    def test_named_register_leaves_default_untouched(self):
        self.assertIsNot(SecurityHandler.user_security, self.named_security)

    def test_register_duplicate_name_raises(self):
        with self.assertRaises(ValueError):
            SecurityHandler.register(CustomerSecurity(OTHER_COOKIE, SECRET_KEY, timedelta(seconds=30)), NAMED_HANDLER)

    def test_get_unknown_name_raises(self):
        with self.assertRaises(ValueError):
            SecurityHandler.get('unknown_handler')

    def test_require_login_runs_named_handler(self):
        # CustomerSecurity answers an admitted request with a 200 response of its own.
        self.assertEqual(self._call_view(NAMED_COOKIE).status_code, 200)

    def test_require_login_named_handler_denies_without_its_cookie(self):
        self.assertNotEqual(self._call_view(OTHER_COOKIE).status_code, 200)


if __name__ == '__main__':
    unittest.main()
