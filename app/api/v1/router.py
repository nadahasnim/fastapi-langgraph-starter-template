from fastapi import APIRouter

from app.api.v1.routes.documents import router as documents_router
from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.responses import router as responses_router

router = APIRouter()
router.include_router(health_router)
router.include_router(responses_router)
router.include_router(documents_router)
