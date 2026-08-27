"""ASGI user-auth middleware for FastAPI / Starlette.

Mirrors the Flask `UserAuthMiddleware` (WSGI) and Django `UserAuthMiddleware`
patterns: read the configured cookie, decode it via the registered
SecurityHandler, and stash the resulting session object on the request
scope so views / dependencies can read it.
"""
from starlette.middleware.base import BaseHTTPMiddleware

from core_lib.session.security_handler import SecurityHandler


class UserAuthMiddleware(BaseHTTPMiddleware):
    """Attach the decoded session object to ``request.state.user`` when
    the configured cookie is present. Use it like any Starlette middleware::

        app.add_middleware(UserAuthMiddleware, cookie_name='my_cookie')
    """

    def __init__(self, app, cookie_name: str):
        super().__init__(app)
        self.cookie_name = cookie_name

    async def dispatch(self, request, call_next):
        token = request.cookies.get(self.cookie_name)
        if token:
            request.state.user = SecurityHandler.get().token_to_session_object(token)
        return await call_next(request)
