from datetime import datetime, timedelta, timezone
import logging
import jwt

from core_lib.session.token_handler import TokenHandler


class JWTTokenHandler(TokenHandler):
    def __init__(self, secret, expiration_time: timedelta, verify: bool = False, algorithm: str = 'HS256'):
        """
        Initialize a JWT token handler with the specified configuration.
        
        Parameters:
            secret: The secret key used for signing and verifying tokens.
            expiration_time (timedelta): Duration before encoded tokens expire.
            verify (bool): Whether to verify token signatures during decoding. Defaults to False.
            algorithm (str): The algorithm to use for encoding and decoding. Defaults to 'HS256'.
        
        Raises:
            AssertionError: If secret or expiration_time are empty or falsy.
        """
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
        """
        Encodes a message as a JWT token.
        
        If an expiration time is configured, the token automatically includes an expiration claim.
        
        Parameters:
        	message (dict): The JWT claims to encode.
        
        Returns:
        	str: The encoded JWT token.
        """
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
        """
        Decode a JWT token using the instance's verification configuration.
        
        Returns:
        	dict: The decoded token payload.
        
        Raises:
        	Exception: Any exception raised during decoding.
        """
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
