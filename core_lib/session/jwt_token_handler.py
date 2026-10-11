from datetime import datetime, timedelta, timezone
import logging
import jwt

from core_lib.session.token_handler import TokenHandler


class JWTTokenHandler(TokenHandler):
    # `verify` is ignored and kept only so existing calls keep working:
    # PyJWT 2 always checks the signature and the expiry.
    def __init__(self, secret, expiration_time: timedelta, verify: bool = False, algorithm: str = 'HS256'):
        assert secret and expiration_time
        self._secret = secret
        self._expiration_time = expiration_time
        self._algorithm = algorithm
        self._logger = logging.getLogger(self.__class__.__name__)

    def encode(self, message: dict) -> str:
        payload = dict(message)
        if self._expiration_time:
            payload['exp'] = datetime.now(timezone.utc) + self._expiration_time

        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def decode(self, encoded):
        try:
            return jwt.decode(encoded, self._secret, algorithms=[self._algorithm])
        except BaseException as e:
            self._logger.error(e)
            raise e
