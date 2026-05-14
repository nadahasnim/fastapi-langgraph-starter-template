"""Request ID middleware for tracing requests."""

from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware that adds or preserves x-request-id header."""

    async def dispatch(self, request: Request, call_next):
        """Process request and add request ID."""
        request_id = request.headers.get("x-request-id") or uuid4().hex
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["x-request-id"] = request_id

        return response
