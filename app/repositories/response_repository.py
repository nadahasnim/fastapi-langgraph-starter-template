from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.response import Response


class ResponseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        conversation_id: str,
        message_id: str | None,
        model: str,
        output: dict,
        metadata: dict,
        extensions: dict,
        response_id: str,
    ) -> Response:
        response = Response(
            id=response_id,
            conversation_id=conversation_id,
            message_id=message_id,
            model=model,
            output=output,
            metadata_json=metadata,
            extensions=extensions,
        )
        self.session.add(response)
        await self.session.flush()
        return response
