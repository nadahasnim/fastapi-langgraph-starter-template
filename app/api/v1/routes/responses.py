from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.responses import ResponseCreateRequest, ResponseObject
from app.db.session import get_session
from app.services.response_service import ResponseService

router = APIRouter(prefix="/responses", tags=["responses"])


@router.post("", response_model=ResponseObject)
async def create_response(
    request: ResponseCreateRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ResponseObject | StreamingResponse:
    service = ResponseService(session=session)
    if request.stream:
        response = await service.create_response(request)
        await session.commit()
        return StreamingResponse(service.stream_events(response), media_type="text/event-stream")

    response = await service.create_response(request)
    await session.commit()
    return response
