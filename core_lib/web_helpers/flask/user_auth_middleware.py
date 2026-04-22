from core_lib.session.security_handler import SecurityHandler


class UserAuthMiddleware:

    def __init__(self, app, cookie_name):
        self.app = app
        self.cookie_name = cookie_name

    def __call__(self, environ, start_response):
        try:
            from flask import Request
        except ImportError:
            raise ImportError("pip install flask to use Flask middleware")
        request = Request(environ)
        if request.cookies.get(self.cookie_name):
            environ['user'] = SecurityHandler.get().token_to_session_object(request.cookies.get(self.cookie_name))

        return self.app(environ, start_response)
