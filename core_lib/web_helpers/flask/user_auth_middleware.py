import os
from datetime import timedelta
from core_lib.session.security_handler import SecurityHandler
from core_lib.web_helpers.flask.admin_security import AdminSecurity


class UserAuthMiddleware():
    def __init__(self):
        self.secret_key = os.environ.get('SECRET_KEY')
        self.security_handler = AdminSecurity('auth_token', self.secret_key, timedelta(days=30))
        SecurityHandler.register(self.security_handler)

    @staticmethod
    def process_request(request):
        if request.cookies.get('auth_token'):
            user = SecurityHandler.get().token_to_session_object(request.cookies.get('auth_token'))
            return user

