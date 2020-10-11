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

    def encode(self, message: dict):
        if 'exp' not in message and self._expiration_time:
            message['exp'] = self._expiration()
        return jwt.encode(message, self._secret, algorithm=self._algorithm).decode("utf-8")

    def decode(self, encoded):
        try:
            return jwt.decode(encoded, self._secret, algorithms=[self._algorithm], exp=self._expiration(), verify=self._verify)
        except BaseException as e:
            self._logger.error(e)
            raise e

    def _expiration(self):
        return (datetime.today() - self._expiration_time).timestamp()
