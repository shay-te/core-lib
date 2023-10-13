from flask import Request
from core_lib.session.security_handler import SecurityHandler


class UserAuthMiddleware:

    def __init__(self, app, cookie_name):
        self.app = app
        self.cookie_name = cookie_name

    def __call__(self, environ, start_response):
        request = Request(environ)
        if request.cookies.get(self.cookie_name):
            environ['user'] = SecurityHandler.get().token_to_session_object(request.cookies.get(self.cookie_name))

        return self.app(environ, start_response)
