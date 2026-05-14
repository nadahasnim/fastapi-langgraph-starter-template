"""Auth stub middleware for parsing authorization headers."""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class AuthStubMiddleware(BaseHTTPMiddleware):
    """Middleware that parses Authorization header without enforcing auth."""

    async def dispatch(self, request: Request, call_next):
        """Parse authorization header and store token in request state."""
        auth_header = request.headers.get("authorization", "")

        if auth_header.startswith("Bearer "):
            request.state.auth_token = auth_header[7:]  # Remove "Bearer " prefix
        else:
            request.state.auth_token = None

        return await call_next(request)
