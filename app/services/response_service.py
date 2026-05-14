import json
from collections.abc import AsyncIterator
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.responses import ResponseCreateRequest, ResponseObject
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.response_repository import ResponseRepository


class ResponseService:
    def __init__(
        self,
        default_model: str = "template-deterministic-model",
        session: AsyncSession | None = None,
    ) -> None:
        self.default_model = default_model
        self.session = session

    async def create_response(self, request: ResponseCreateRequest) -> ResponseObject:
        model = request.model or self.default_model
        response = ResponseObject.create_text_response(
            response_id=f"resp_{uuid4().hex}",
            model=model,
            text=f"Template response: {request.input}",
            metadata=request.metadata,
        )

        if self.session is not None:
            conversation = await self._get_or_create_conversation(request)
            message = await MessageRepository(self.session).create(
                conversation_id=conversation.id,
                role="user",
                content=request.input,
                metadata=request.metadata,
            )
            await ResponseRepository(self.session).create(
                conversation_id=conversation.id,
                message_id=message.id,
                model=response.model,
                output=response.model_dump()["output"],
                metadata=response.metadata,
                extensions=response.extensions,
                response_id=response.id,
            )

        return response

    async def stream_response(self, request: ResponseCreateRequest) -> AsyncIterator[str]:
        response = await self.create_response(request)
        async for event in self.stream_events(response):
            yield event

    async def stream_events(self, response: ResponseObject) -> AsyncIterator[str]:
        text = response.output[0].content[0].text
        yield self._sse("response.created", {"id": response.id, "model": response.model})
        yield self._sse("response.output_text.delta", {"delta": text})
        yield self._sse("response.output_text.done", {"text": text})
        yield self._sse("response.completed", response.model_dump())

    async def _get_or_create_conversation(self, request: ResponseCreateRequest):
        repository = ConversationRepository(self.session)
        if request.conversation_id is not None:
            conversation = await repository.get(request.conversation_id)
            if conversation is not None:
                return conversation

        user_id = request.metadata.get("user_id")
        title = request.input[:80]
        return await repository.create(user_id=user_id, title=title)

    @staticmethod
    def _sse(event: str, data: dict) -> str:
        return f"event: {event}\ndata: {json.dumps(data)}\n\n"
