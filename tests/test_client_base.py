"""ClientBase joins the base URL and path, and applies its headers, timeout and auth to every call on one session."""
import json
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests

from core_lib.client.client_base import ClientBase

SLOW_SECONDS = 0.5


class _EchoHandler(BaseHTTPRequestHandler):
    # Answers every request with what it received, as JSON. HTTP/1.1, so one session can keep its connection.
    protocol_version = 'HTTP/1.1'

    def _echo(self):
        if self.path.startswith('/slow'):
            time.sleep(SLOW_SECONDS)
        length = int(self.headers.get('Content-Length') or 0)
        payload = json.dumps({
            'method': self.command,
            'path': self.path,
            'headers': {name.lower(): value for name, value in self.headers.items()},
            'body': self.rfile.read(length).decode('utf-8'),
            'client_port': self.client_address[1],
        }).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(payload)))
        if self.path == '/login':
            self.send_header('Set-Cookie', 'session=acme-session; Path=/')
        self.end_headers()
        self.wfile.write(payload)

    do_GET = do_POST = do_PUT = do_DELETE = _echo

    def log_message(self, format, *args):
        pass   # keep the test output clean


class _QuietServer(ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address):
        pass   # a client that timed out closes its socket before the slow answer is written


class WidgetClient(ClientBase):
    def get(self, widget_id: int) -> dict:
        return self._get(f'/widgets/{widget_id}').json()

    def search(self, name: str) -> dict:
        return self._get('widgets', params={'name': name}).json()

    def create(self, data: dict) -> dict:
        return self._post('/widgets', json=data).json()

    def update(self, widget_id: int, data: dict) -> dict:
        return self._put(f'/widgets/{widget_id}', data=data).json()

    def delete(self, widget_id: int) -> dict:
        return self._delete(f'/widgets/{widget_id}').json()

    def get_with(self, path: str, **kwargs) -> dict:
        return self._get(path, **kwargs).json()


class TestClientBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.server = _QuietServer(('127.0.0.1', 0), _EchoHandler)
        cls.base_url = f'http://127.0.0.1:{cls.server.server_address[1]}'
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_each_method_sends_its_verb_to_the_joined_url(self):
        # A trailing `/` on the base URL and a leading `/` on the path collapse to one; `/v1` is kept.
        client = WidgetClient(f'{self.base_url}/v1/')

        got = client.get(7)
        self.assertEqual(('GET', '/v1/widgets/7', ''), (got['method'], got['path'], got['body']))

        searched = client.search('acme widget')
        self.assertEqual(('GET', '/v1/widgets?name=acme+widget'), (searched['method'], searched['path']))

        created = client.create({'name': 'acme'})
        self.assertEqual(('POST', '/v1/widgets'), (created['method'], created['path']))
        self.assertEqual({'name': 'acme'}, json.loads(created['body']))
        self.assertEqual('application/json', created['headers']['content-type'])

        updated = client.update(7, {'name': 'acme'})
        self.assertEqual(('PUT', '/v1/widgets/7', 'name=acme'), (updated['method'], updated['path'], updated['body']))
        self.assertEqual('application/x-www-form-urlencoded', updated['headers']['content-type'])

        deleted = client.delete(7)
        self.assertEqual(('DELETE', '/v1/widgets/7'), (deleted['method'], deleted['path']))

    def test_nothing_is_added_until_configured(self):
        got = WidgetClient(self.base_url).get_with('/widgets', headers={'X-Request-Id': 'req-1'})

        self.assertEqual('req-1', got['headers']['x-request-id'])
        self.assertNotIn('authorization', got['headers'])
        self.assertNotIn('x-tenant', got['headers'])

    def test_client_headers_go_on_every_call_and_win_over_call_headers(self):
        client = WidgetClient(self.base_url)
        client.set_headers({'Authorization': 'Bearer acme-token', 'X-Tenant': 'acme'})
        call_headers = {'X-Tenant': 'other', 'X-Request-Id': 'req-1'}

        merged = client.get_with('/widgets', headers=call_headers)
        plain = client.get(7)

        self.assertEqual('Bearer acme-token', merged['headers']['authorization'])
        self.assertEqual('acme', merged['headers']['x-tenant'])
        self.assertEqual('req-1', merged['headers']['x-request-id'])
        self.assertEqual({'X-Tenant': 'other', 'X-Request-Id': 'req-1'}, call_headers)   # the caller's dict is untouched
        self.assertEqual('Bearer acme-token', plain['headers']['authorization'])
        self.assertEqual('acme', plain['headers']['x-tenant'])

    def test_auth_goes_on_every_call_and_replaces_call_auth(self):
        client = WidgetClient(self.base_url)
        client.set_auth(('reviewer', 's3cret'))

        got = client.get(7)
        overridden = client.get_with('/widgets', auth=('other', 'password'))

        self.assertEqual('Basic cmV2aWV3ZXI6czNjcmV0', got['headers']['authorization'])        # reviewer:s3cret
        self.assertEqual('Basic cmV2aWV3ZXI6czNjcmV0', overridden['headers']['authorization'])

    def test_timeout_applies_to_every_call_and_a_call_timeout_wins(self):
        client = WidgetClient(self.base_url)
        client.set_timeout(SLOW_SECONDS / 5)

        with self.assertRaises(requests.exceptions.Timeout):
            client.get_with('/slow')
        self.assertEqual('/slow', client.get_with('/slow', timeout=SLOW_SECONDS * 10)['path'])
        self.assertEqual('/widgets/7', client.get(7)['path'])   # a fast call is within the client timeout

    def test_one_session_keeps_its_connection_and_cookies(self):
        client = WidgetClient(self.base_url)

        login = client.get_with('/login')
        first = client.get(1)
        second = client.get(2)

        self.assertNotIn('cookie', login['headers'])
        self.assertEqual('session=acme-session', first['headers']['cookie'])
        self.assertEqual('session=acme-session', second['headers']['cookie'])
        self.assertEqual(login['client_port'], first['client_port'])   # the same pooled connection
        self.assertEqual(first['client_port'], second['client_port'])
        self.assertNotIn('cookie', WidgetClient(self.base_url).get(3)['headers'])   # a second client has its own session
