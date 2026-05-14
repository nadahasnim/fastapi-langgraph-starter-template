"""Error handler middleware for structured error responses."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.errors import AppError


def register_error_handlers(app: FastAPI) -> None:
    """Register error handlers for the application."""

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        """Handle AppError exceptions with structured JSON response."""
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions with generic error response."""
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "internal_error", "message": "Internal server error"}},
        )
