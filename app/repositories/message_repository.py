from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.message import Message


class MessageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self, conversation_id: str, role: str, content: str, metadata: dict
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            metadata_json=metadata,
        )
        self.session.add(message)
        await self.session.flush()
        return message
