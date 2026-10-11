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


@unittest.skipUnless(hasattr(time, 'tzset'), 'time.tzset() is needed to change the process time zone')
class TestJWTTokenHandler(unittest.TestCase):

    def setUp(self):
        self._original_tz = os.environ.get('TZ')

    def tearDown(self):
        if self._original_tz is None:
            os.environ.pop('TZ', None)
        else:
            os.environ['TZ'] = self._original_tz
        time.tzset()

    def _use_time_zone(self, zone: str):
        os.environ['TZ'] = zone
        time.tzset()

    def test_exp_is_an_hour_from_now_in_every_time_zone(self):
        for zone in NON_UTC_ZONES + ['UTC']:
            self._use_time_zone(zone)
            token_handler = JWTTokenHandler(SECRET, timedelta(hours=1))

            before = time.time()
            token = token_handler.encode({'user_id': 7})
            after = time.time()

            exp = jwt.decode(token, options={'verify_signature': False})['exp']
            self.assertGreaterEqual(exp, int(before) + 3600, zone)
            self.assertLessEqual(exp, after + 3600, zone)

    def test_token_issued_in_a_non_utc_zone_decodes(self):
        for zone in NON_UTC_ZONES:
            self._use_time_zone(zone)
            token_handler = JWTTokenHandler(SECRET, timedelta(hours=1))

            payload = token_handler.decode(token_handler.encode({'user_id': 7}))

            self.assertEqual(7, payload['user_id'], zone)

    def test_encode_does_not_change_the_callers_dict(self):
        session_data = {'user_id': 7}

        JWTTokenHandler(SECRET, timedelta(hours=1)).encode(session_data)

        self.assertEqual({'user_id': 7}, session_data)

    def test_expired_token_raises(self):
        token_handler = JWTTokenHandler(SECRET, timedelta(seconds=1))
        token = token_handler.encode({'user_id': 7})
        time.sleep(2.1)
        with self.assertRaises(jwt.ExpiredSignatureError):
            token_handler.decode(token)

    def test_token_signed_with_another_secret_raises(self):
        token = JWTTokenHandler('another-widget-secret-0123456789abcdef', timedelta(hours=1)).encode({'user_id': 7})
        with self.assertRaises(jwt.InvalidSignatureError):
            JWTTokenHandler(SECRET, timedelta(hours=1)).decode(token)

    def test_decode_emits_no_deprecation_warning(self):
        token_handler = JWTTokenHandler(SECRET, timedelta(hours=1))
        token = token_handler.encode({'user_id': 7})
        with warnings.catch_warnings():
            warnings.simplefilter('error')
            self.assertEqual(7, token_handler.decode(token)['user_id'])
