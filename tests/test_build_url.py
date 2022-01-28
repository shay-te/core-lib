import unittest

from core_lib.data_layers.data.data_helpers import build_url


class TestBuildUrl(unittest.TestCase):

    def test_build_url(self):
        self.assertEqual(build_url(host="some_domain.com"), "some_domain.com")
        self.assertEqual(build_url(protocol="http", host="some_domain.com"), "http://some_domain.com")
        self.assertEqual(build_url(protocol="http", host="some_domain.com", username="shay"), "http://shay@some_domain.com")
        self.assertEqual(build_url(protocol="http", host="some_domain.com", username="shay", password="pass"), "http://shay:pass@some_domain.com")
        self.assertEqual(build_url(protocol="http", host="some_domain.com", username="shay", password="pass", port=80), "http://shay:pass@some_domain.com:80")
        self.assertEqual(build_url(protocol="http", host="some_domain.com", username="shay", password="pass", port=80, path="x/y/z"), "http://shay:pass@some_domain.com:80/x/y/z")

        params = {
            "protocol": "http",
            "host": "some_domain.com",
            "username": "shay",
            "password": "pass",
            "port": 80,
            "path": "/x/y/z",
            "file": "file.foo"
        }

        self.assertEqual(build_url(**params), "http://shay:pass@some_domain.com:80/x/y/z/file.foo")
