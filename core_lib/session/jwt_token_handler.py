from datetime import datetime
from datetime import timedelta
import logging
import jwt

from core_lib.session.token_handler import TokenHandler


class JWTTokenHandler(TokenHandler):
    def __init__(self, secret, expiration_time: timedelta, verify: bool = False, algorithm: str = 'HS256'):
        assert secret and expiration_time
        self._secret = secret
        self._expiration_time = expiration_time
        self._verify = verify
        self._algorithm = algorithm
        self._logger = logging.getLogger(self.__class__.__name__)

    def encode(self, message: dict) -> str:
        if self._expiration_time:
            message['exp'] = (datetime.utcnow() + self._expiration_time).timestamp()

        return jwt.encode(message, self._secret, algorithm=self._algorithm)

    def decode(self, encoded):
        try:
            return jwt.decode(encoded, self._secret, algorithms=[self._algorithm], verify=self._verify)
        except BaseException as e:
            self._logger.error(e)
            raise e
