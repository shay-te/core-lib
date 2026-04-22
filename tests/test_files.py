import hashlib
import io
import os
import re
import tempfile
import unittest
from unittest.mock import MagicMock

from core_lib.helpers.files import get_file_md5, download_file_handle


class TestGetFileMd5(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False)
        self.tmp.write(b'hello world')
        self.tmp.flush()
        self.tmp.close()

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_returns_valid_md5_hex(self):
        regex = r'([a-fA-F\d]{32})'
        image_file = os.path.join(os.path.dirname(__file__), 'test_data/koala.jpeg')
        other_file = os.path.join(os.path.dirname(__file__), 'test_files.py')
        self.assertIsNotNone(re.match(regex, get_file_md5(other_file)))
        self.assertIsNotNone(re.match(regex, get_file_md5(image_file)))

    def test_returns_32_char_hex_string(self):
        result = get_file_md5(self.tmp.name)
        self.assertEqual(len(result), 32)
        self.assertTrue(all(c in '0123456789abcdef' for c in result))

    def test_known_content_matches_expected_md5(self):
        expected = hashlib.md5(b'hello world').hexdigest()
        self.assertEqual(get_file_md5(self.tmp.name), expected)

    def test_different_files_different_md5(self):
        with tempfile.NamedTemporaryFile(delete=False) as f2:
            f2.write(b'different content')
            f2.flush()
            name2 = f2.name
        try:
            self.assertNotEqual(get_file_md5(self.tmp.name), get_file_md5(name2))
        finally:
            os.unlink(name2)

    def test_same_file_same_md5(self):
        self.assertEqual(get_file_md5(self.tmp.name), get_file_md5(self.tmp.name))

    def test_empty_file_has_known_md5(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            empty_name = f.name
        try:
            expected = hashlib.md5(b'').hexdigest()
            self.assertEqual(get_file_md5(empty_name), expected)
        finally:
            os.unlink(empty_name)

    def test_binary_file(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as f:
            f.write(bytes(range(256)))
            bin_name = f.name
        try:
            result = get_file_md5(bin_name)
            self.assertEqual(len(result), 32)
        finally:
            os.unlink(bin_name)

    def test_nonexistent_file_raises(self):
        self.assertRaises(FileNotFoundError, get_file_md5, '/nonexistent/path/file.txt')


class TestDownloadFileHandle(unittest.TestCase):
    def _make_response(self, chunks):
        response = MagicMock()
        response.__enter__ = lambda s: s
        response.__exit__ = MagicMock(return_value=False)
        response.raise_for_status = MagicMock()
        response.iter_content = MagicMock(return_value=iter(chunks))
        return response

    def test_writes_chunks_to_file_handle(self):
        response = self._make_response([b'hello', b' ', b'world'])
        buf = io.BytesIO()
        download_file_handle(response, buf)
        buf.seek(0)
        self.assertEqual(buf.read(), b'hello world')

    def test_empty_chunks_not_written(self):
        response = self._make_response([b'data', b'', b'more'])
        buf = io.BytesIO()
        download_file_handle(response, buf)
        buf.seek(0)
        self.assertEqual(buf.read(), b'datamore')

    def test_raise_for_status_is_called(self):
        response = self._make_response([b'ok'])
        buf = io.BytesIO()
        download_file_handle(response, buf)
        response.raise_for_status.assert_called_once()

    def test_single_large_chunk(self):
        data = b'x' * 8192
        response = self._make_response([data])
        buf = io.BytesIO()
        download_file_handle(response, buf)
        buf.seek(0)
        self.assertEqual(buf.read(), data)

    def test_no_chunks_writes_nothing(self):
        response = self._make_response([])
        buf = io.BytesIO()
        download_file_handle(response, buf)
        buf.seek(0)
        self.assertEqual(buf.read(), b'')

    def test_http_error_propagates(self):
        from requests.exceptions import HTTPError
        response = MagicMock()
        response.__enter__ = lambda s: s
        response.__exit__ = MagicMock(return_value=False)
        response.raise_for_status = MagicMock(side_effect=HTTPError('404'))
        response.iter_content = MagicMock(return_value=iter([]))
        buf = io.BytesIO()
        self.assertRaises(HTTPError, download_file_handle, response, buf)
