
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.document import Document


class DocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        user_id: str,
        filename: str,
        content_type: str,
        source: str,
    ) -> Document:
        document = Document(
            user_id=user_id,
            filename=filename,
            content_type=content_type,
            source=source,
        )
        self.session.add(document)
        await self.session.flush()
        return document

    async def get(self, document_id: str) -> Document | None:
        return await self.session.get(Document, document_id)
