import io
import os
import re
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests

from core_lib.helpers.files import download_file, download_file_handle, get_file_md5

# Larger than two of download_file_handle's 8 KB chunks, with every byte value in it.
REPORT_BYTES = bytes(range(256)) * 78 + b'acme-widget-report'


class _ReportHandler(BaseHTTPRequestHandler):
    # Serves one file at /reports/widgets.bin; any other path is a 404, /broken is a 500.

    def do_GET(self):
        if self.path == '/reports/widgets.bin':
            status, body = 200, REPORT_BYTES
        elif self.path == '/broken':
            status, body = 500, b'acme storage is down'
        else:
            status, body = 404, b'no such report'
        self.send_response(status)
        self.send_header('Content-Type', 'application/octet-stream')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass   # keep the test output clean


class TestFiles(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), _ReportHandler)
        cls.server.daemon_threads = True
        cls.base_url = f'http://127.0.0.1:{cls.server.server_address[1]}'
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_get_file_md5(self):
        regex = r"([a-fA-F\d]{32})"
        image_file = os.path.join(os.path.dirname(__file__), 'test_data/koala.jpeg')
        other_file = os.path.join(os.path.dirname(__file__), 'test_files.py')
        self.assertIsNotNone(re.match(regex, get_file_md5(other_file)))
        self.assertIsNotNone(re.match(regex, get_file_md5(image_file)))

    def test_get_file_md5_known_digests(self):
        with tempfile.TemporaryDirectory() as folder:
            hello_path = os.path.join(folder, 'hello.txt')
            empty_path = os.path.join(folder, 'empty.txt')
            with open(hello_path, 'wb') as file_handle:
                file_handle.write(b'hello\n')
            open(empty_path, 'wb').close()

            self.assertEqual('b1946ac92492d2347c6235b4d2611184', get_file_md5(hello_path))
            self.assertEqual('d41d8cd98f00b204e9800998ecf8427e', get_file_md5(empty_path))

    def test_download_file_writes_every_byte(self):
        with tempfile.TemporaryDirectory() as folder:
            local_path = os.path.join(folder, 'widgets.bin')

            download_file(f'{self.base_url}/reports/widgets.bin', local_path)

            with open(local_path, 'rb') as file_handle:
                self.assertEqual(REPORT_BYTES, file_handle.read())

    def test_download_file_http_error_raises_and_leaves_an_empty_file(self):
        with tempfile.TemporaryDirectory() as folder:
            local_path = os.path.join(folder, 'missing.bin')

            with self.assertRaises(requests.HTTPError) as context:
                download_file(f'{self.base_url}/reports/missing.bin', local_path)

            self.assertEqual(404, context.exception.response.status_code)
            self.assertEqual(0, os.path.getsize(local_path))

    def test_download_file_handle_streams_into_any_writable(self):
        response = requests.get(f'{self.base_url}/reports/widgets.bin', stream=True)
        buffer = io.BytesIO()

        download_file_handle(response, buffer)

        self.assertEqual(REPORT_BYTES, buffer.getvalue())

    def test_download_file_handle_raises_before_writing(self):
        response = requests.get(f'{self.base_url}/broken', stream=True)
        buffer = io.BytesIO()

        with self.assertRaises(requests.HTTPError) as context:
            download_file_handle(response, buffer)

        self.assertEqual(500, context.exception.response.status_code)
        self.assertEqual(b'', buffer.getvalue())
