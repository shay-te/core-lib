from core_lib.session.user_security import UserSecurity


class SecurityHandler(object):
    user_security = None

    @staticmethod
    def register(user_security: UserSecurity):
        if SecurityHandler.user_security:
            raise ValueError("SecurityHandler already set")
        SecurityHandler.user_security = user_security

    @staticmethod
    def get():
        if not SecurityHandler.user_security:
            raise ValueError("SecurityHandler was not set")
        return SecurityHandler.user_security
