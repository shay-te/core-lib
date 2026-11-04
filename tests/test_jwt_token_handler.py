"""JWTTokenHandler stamps `exp` as an absolute epoch, so a new token is valid for its lifetime in any time zone."""
import os
import time
import unittest
from datetime import timedelta

import jwt

from core_lib.session.jwt_token_handler import JWTTokenHandler

SECRET = 'jwt-handler-secret'
LIFETIME = timedelta(seconds=60)
EAST_OF_UTC = 'Asia/Tokyo'  # UTC+9 all year


@unittest.skipUnless(hasattr(time, 'tzset'), 'time.tzset is Unix only')
class TestJWTTokenHandler(unittest.TestCase):

    def setUp(self):
        # Every machine runs this east of UTC, CI included: there, a naive UTC time read as local time lands
        # hours in the past.
        self.addCleanup(self._set_time_zone, os.environ.get('TZ'))
        self._set_time_zone(EAST_OF_UTC)

    @staticmethod
    def _set_time_zone(name):
        if name is None:
            os.environ.pop('TZ', None)
        else:
            os.environ['TZ'] = name
        time.tzset()

    def test_new_token_decodes(self):
        handler = JWTTokenHandler(SECRET, LIFETIME)
        self.assertEqual(7, handler.decode(handler.encode({'id': 7}))['id'])

    def test_exp_is_now_plus_lifetime(self):
        token = JWTTokenHandler(SECRET, LIFETIME).encode({'id': 7})
        exp = jwt.decode(token, options={'verify_signature': False})['exp']
        self.assertAlmostEqual(time.time() + LIFETIME.total_seconds(), exp, delta=5)
