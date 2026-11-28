from starlette.middleware.base import BaseHTTPMiddleware

from core_lib.session.security_handler import SecurityHandler


class UserAuthMiddleware(BaseHTTPMiddleware):
    """Puts the session object from the cookie on `request.state.user`, like the Flask and Django versions."""

    def __init__(self, app, cookie_name: str):
        super().__init__(app)
        self.cookie_name = cookie_name

    async def dispatch(self, request, call_next):
        cookie_value = request.cookies.get(self.cookie_name)
        if cookie_value:
            request.state.user = SecurityHandler.get().token_to_session_object(cookie_value)
        return await call_next(request)
