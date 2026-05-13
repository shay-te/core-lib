from datetime import datetime, timedelta, timezone
import logging
import jwt

from core_lib.session.token_handler import TokenHandler


class JWTTokenHandler(TokenHandler):
    def __init__(self, secret, expiration_time: timedelta, verify: bool = False, algorithm: str = 'HS256'):
        if not secret:
            raise AssertionError('JWTTokenHandler: secret is required')
        if not expiration_time:
            raise AssertionError('JWTTokenHandler: expiration_time is required')
        self._secret = secret
        self._expiration_time = expiration_time
        self._verify = verify
        self._algorithm = algorithm
        self._logger = logging.getLogger(self.__class__.__name__)

    def encode(self, message: dict) -> str:
        if self._expiration_time:
            message['exp'] = (datetime.now(tz=timezone.utc) + self._expiration_time).timestamp()

        return jwt.encode(message, self._secret, algorithm=self._algorithm)

    def decode(self, encoded):
        # PyJWT 2.0+ deprecated the `verify` keyword; passing it does nothing
        # AND emits a DeprecationWarning on every call. The equivalent now is
        # `options={'verify_signature': False}`. We keep the historic claim
        # checks (exp / nbf / iat / aud / iss) ON even when verify=False,
        # because PyJWT cascades `verify_signature=False` to auto-disable all
        # other claim verifications by default — which is more permissive
        # than what callers of `verify=False` expect.
        if self._verify:
            options = {}
        else:
            options = {
                'verify_signature': False,
                'verify_exp': True,
                'verify_nbf': True,
                'verify_iat': True,
                'verify_aud': True,
                'verify_iss': True,
                'verify_sub': True,
                'verify_jti': True,
            }
        try:
            return jwt.decode(
                encoded,
                self._secret,
                algorithms=[self._algorithm],
                options=options,
            )
        except Exception as e:
            self._logger.error(e)
            raise e
