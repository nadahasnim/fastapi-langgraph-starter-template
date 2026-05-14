from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.conversation import Conversation


class ConversationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, user_id: str | None, title: str | None = None) -> Conversation:
        conversation = Conversation(user_id=user_id, title=title)
        self.session.add(conversation)
        await self.session.flush()
        return conversation

    async def get(self, conversation_id: str) -> Conversation | None:
        return await self.session.get(Conversation, conversation_id)
