from flask import Request
from core_lib.session.security_handler import SecurityHandler


class UserAuthMiddleware():

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request = Request(environ)
        if request.cookies.get('auth_token'):
            environ['user'] = SecurityHandler.get().token_to_session_object(request.cookies.get('auth_token'))

        return self.app(environ, start_response)
