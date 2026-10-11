"""The [flask] extra alone runs the Flask web helpers, and the [django] extra alone runs the Django ones."""
import os
import subprocess
import sys
import textwrap
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OTHER_EXTRAS = [
    'psycopg2', 'pymysql', 'pymongo', 'mongomock', 'pysolr', 'neo4j', 'redis', 'memcache', 'elasticsearch',
    'geoalchemy2', 'shapely', 'numpy', 'pandas', 'boto3', 'moto', 'freezegun', 'flask_wtf',
]
FLASK_ONLY = ['flask', 'flask_cors', 'werkzeug']

FLASK_SCRIPT = textwrap.dedent('''
    from http import HTTPStatus
    from flask import Flask
    from core_lib.error_handling.status_code_exception import StatusCodeException
    from core_lib.web_helpers.decorators import HandleException
    from core_lib.web_helpers.flask.require_login import RequireLogin
    from core_lib.web_helpers.flask.user_auth_middleware import UserAuthMiddleware
    from core_lib.web_helpers.request_response_helpers import response_json
    from core_lib.web_helpers.web_helpers_utils import WebHelpersUtils

    WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)
    app = Flask('acme')

    @app.get('/widgets/<int:widget_id>')
    @HandleException()
    def get_widget(widget_id):
        if widget_id != 1:
            raise StatusCodeException(HTTPStatus.NOT_FOUND)
        return response_json({'id': 1})

    client = app.test_client()
    print(client.get('/widgets/1').status_code, client.get('/widgets/2').status_code)
''')

DJANGO_SCRIPT = textwrap.dedent('''
    from http import HTTPStatus
    from django.conf import settings
    settings.configure(COOKIE_NAME='acme_cookie')
    from core_lib.error_handling.status_code_exception import StatusCodeException
    from core_lib.web_helpers.decorators import HandleException
    from core_lib.web_helpers.django.require_login import RequireLogin
    from core_lib.web_helpers.django.user_auth_middleware import UserAuthMiddleware
    from core_lib.web_helpers.request_response_helpers import response_json
    from core_lib.web_helpers.web_helpers_utils import WebHelpersUtils

    WebHelpersUtils.init(WebHelpersUtils.ServerType.DJANGO)

    @HandleException()
    def get_widget(request, widget_id):
        if widget_id != 1:
            raise StatusCodeException(HTTPStatus.NOT_FOUND)
        return response_json({'id': 1})

    print(get_widget(None, 1).status_code, get_widget(None, 2).status_code)
''')


def run_without(blocked: list, script: str) -> subprocess.CompletedProcess:
    prelude = 'import sys\n' + ''.join(f'sys.modules[{name!r}] = None\n' for name in blocked)
    environment = dict(os.environ, PYTHONPATH=REPO_ROOT)
    return subprocess.run(
        [sys.executable, '-c', prelude + script], cwd=REPO_ROOT, env=environment, capture_output=True, text=True, timeout=120
    )


class TestWebExtraInstall(unittest.TestCase):

    def test_flask_helpers_run_without_django(self):
        result = run_without(OTHER_EXTRAS + ['django'], FLASK_SCRIPT)

        self.assertEqual(0, result.returncode, result.stderr[-3000:])
        self.assertEqual('200 404', result.stdout.strip().splitlines()[-1])

    def test_django_helpers_run_without_flask(self):
        result = run_without(OTHER_EXTRAS + FLASK_ONLY, DJANGO_SCRIPT)

        self.assertEqual(0, result.returncode, result.stderr[-3000:])
        self.assertEqual('200 404', result.stdout.strip().splitlines()[-1])
