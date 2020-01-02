import datetime
import logging

import jwt

days_to_subtract = 1


class SessionManager(object):

    __instance = None

    def __init__(self, secret):
        self.secret = secret
        self.logger = logging.getLogger(self.__class__.__name__)

    @staticmethod
    def init(secret):
        if SessionManager.__instance is None:
            SessionManager.__instance = SessionManager(secret)

    @staticmethod
    def get():
        if SessionManager.__instance is None:
            raise NameError('SessionManager not initialized')
        return SessionManager.__instance

    def encode(self, user_id, facebook_id):
        message = {
            'user_id': user_id,
            'facebook_id': facebook_id,
            'exp': self.__expiration()
        }
        return jwt.encode(message, self.secret, algorithm='HS256').decode("utf-8")

    def decode(self, encoded):
        try:
            # check what with verify=False
            return jwt.decode(encoded, self.secret, algorithms=['HS256'], exp=self.__expiration(), verify=False)
        except jwt.ExpiredSignatureError as e:
            # LOG INGO
            self.logger.error(e)

            return None
            # raise IOError('Error decoding jwt') from e
        # except jwt.InvalidTokenError:
        #     return 'Invalid token. Please log in again.'

    def __expiration(self):
        return datetime.datetime.today() - datetime.timedelta(days=days_to_subtract)
