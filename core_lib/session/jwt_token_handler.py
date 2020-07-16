from datetime import datetime
from datetime import timedelta
import logging
import jwt

from core_lib.session.token_handler import TokenHandler


class JWTTokenHandler(TokenHandler):

    def __init__(self, secret, expiration_time: timedelta, verify: bool = False):
        assert secret and expiration_time
        self._secret = secret
        self._expiration_time = expiration_time
        self._verify = verify
        self._logger = logging.getLogger(self.__class__.__name__)

    def encode(self, message: dict):
        message['exp'] = self._expiration()
        return jwt.encode(message, self._secret, algorithm='HS256').decode("utf-8")

    def decode(self, encoded):
        try:
            return jwt.decode(encoded, self._secret, algorithms=['HS256'], exp=self._expiration(), verify=self._verify)
        except BaseException as e:
            self._logger.error(e)
            raise e

    def _expiration(self):
        return datetime.today() - self._expiration_time
