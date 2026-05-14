from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any, Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.orchestrator.graph import OrchestratorGraph
from app.agents.shared.events import (
    RESPONSE_COMPLETED,
    RESPONSE_CREATED,
    RESPONSE_OUTPUT_TEXT_DELTA,
    RESPONSE_OUTPUT_TEXT_DONE,
)
from app.agents.shared.llm import OpenRouterLlmProvider
from app.api.v1.schemas.responses import ResponseCreateRequest, ResponseObject
from app.core.config import get_settings
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.response_repository import ResponseRepository


class ResponseOrchestrator(Protocol):
    async def invoke(
        self, input_text: str, metadata: dict[str, Any], model: str | None = None
    ) -> ResponseObject: ...


class ResponseService:
    def __init__(
        self,
        default_model: str = "template-deterministic-model",
        session: AsyncSession | None = None,
        orchestrator: ResponseOrchestrator | None = None,
    ) -> None:
        settings = get_settings()
        self.default_model = default_model or settings.default_chat_model
        self.session = session
        self.orchestrator = orchestrator or self._build_default_orchestrator()

    async def create_response(self, request: ResponseCreateRequest) -> ResponseObject:
        request = ResponseCreateRequest.model_validate(request)
        response = ResponseObject.model_validate(
            await self.orchestrator.invoke(request.input, dict(request.metadata), request.model)
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
        yield self._sse(RESPONSE_CREATED, {"id": response.id, "model": response.model})
        yield self._sse(RESPONSE_OUTPUT_TEXT_DELTA, {"delta": text})
        yield self._sse(RESPONSE_OUTPUT_TEXT_DONE, {"text": text})
        yield self._sse(RESPONSE_COMPLETED, response.model_dump())

    async def _get_or_create_conversation(self, request: ResponseCreateRequest):
        assert self.session is not None
        repository = ConversationRepository(self.session)
        if request.conversation_id is not None:
            conversation = await repository.get(request.conversation_id)
            if conversation is not None:
                return conversation

        user_id = request.metadata.get("user_id")
        title = request.input[:80]
        return await repository.create(user_id=user_id, title=title)

    @staticmethod
    def _sse(event: str, data: dict[str, Any]) -> str:
        return f"event: {event}\ndata: {json.dumps(data)}\n\n"

    def _build_default_orchestrator(self) -> OrchestratorGraph:
        settings = get_settings()
        return OrchestratorGraph(
            llm_provider=OpenRouterLlmProvider(settings=settings),
            default_model=self.default_model or settings.default_chat_model,
        )
