from core_lib.session.user_security import UserSecurity


class SecurityHandler(object):
    user_security = None
    named_user_securities = {}

    @staticmethod
    def register(user_security: UserSecurity, name: str = None):
        if name:
            if name in SecurityHandler.named_user_securities:
                raise ValueError(f"SecurityHandler `{name}` already set")
            SecurityHandler.named_user_securities[name] = user_security
            return
        if SecurityHandler.user_security:
            raise ValueError("SecurityHandler already set")
        SecurityHandler.user_security = user_security

    @staticmethod
    def get(name: str = None) -> UserSecurity:
        if name:
            if name not in SecurityHandler.named_user_securities:
                raise ValueError(f"SecurityHandler `{name}` was not set")
            return SecurityHandler.named_user_securities[name]
        if not SecurityHandler.user_security:
            raise ValueError("SecurityHandler was not set")
        return SecurityHandler.user_security
