from fastapi import FastAPI

from app.api.v1.router import router as v1_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.middleware.error_handler import register_error_handlers
from app.middleware.request_id import RequestIDMiddleware


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.app_debug,
        version="0.1.0",
    )

    register_error_handlers(app)
    app.add_middleware(RequestIDMiddleware)
    app.include_router(v1_router, prefix="/v1")
    return app


app = create_app()
