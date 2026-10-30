"""JWTTokenHandler sets `exp` from real UTC time in any server time zone and never changes the caller's dict."""
import os
import time
import unittest
import warnings
from datetime import timedelta

import jwt

from core_lib.session.jwt_token_handler import JWTTokenHandler

SECRET = 'acme-widget-secret-0123456789abcdef'   # 32+ bytes, so PyJWT has no key-length warning
NON_UTC_ZONES = ['Asia/Tokyo', 'America/New_York']   # UTC+9 and UTC-5/-4


class TestJWTTokenHandler(unittest.TestCase):

    def setUp(self):
        self._original_tz = os.environ.get('TZ')

    def tearDown(self):
        if self._original_tz is None:
            os.environ.pop('TZ', None)
        else:
            os.environ['TZ'] = self._original_tz
        if hasattr(time, 'tzset'):
            time.tzset()

    @unittest.skipUnless(hasattr(time, 'tzset'), 'time.tzset() is needed to change the process time zone')
    def test_exp_is_an_hour_from_now_in_every_time_zone(self):
        for zone in NON_UTC_ZONES + ['UTC']:
            os.environ['TZ'] = zone
            time.tzset()
            token_handler = JWTTokenHandler(SECRET, timedelta(hours=1))

            before = time.time()
            token = token_handler.encode({'user_id': 7})
            after = time.time()

            exp = jwt.decode(token, options={'verify_signature': False})['exp']
            self.assertGreaterEqual(exp, int(before) + 3600, zone)
            self.assertLessEqual(exp, after + 3600, zone)

    def test_encode_does_not_change_the_callers_dict(self):
        session_data = {'user_id': 7}

        JWTTokenHandler(SECRET, timedelta(hours=1)).encode(session_data)

        self.assertEqual({'user_id': 7}, session_data)

    def test_decode_emits_no_deprecation_warning(self):
        token_handler = JWTTokenHandler(SECRET, timedelta(hours=1))
        token = token_handler.encode({'user_id': 7})
        with warnings.catch_warnings():
            warnings.simplefilter('error')
            self.assertEqual(7, token_handler.decode(token)['user_id'])
