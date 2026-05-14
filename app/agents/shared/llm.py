from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass
from typing import Any, Protocol, cast

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from app.core.config import Settings, get_settings


@dataclass
class LlmMessage:
    role: str
    content: str


@dataclass
class LlmResponse:
    text: str
    model: str


class LlmProvider(Protocol):
    async def complete(
        self, messages: Sequence[LlmMessage], model: str | None = None
    ) -> LlmResponse: ...

    def stream(
        self, messages: Sequence[LlmMessage], model: str | None = None
    ) -> AsyncIterator[str]: ...


class MockLlmProvider:
    def __init__(
        self,
        response_text: str | None = None,
        model: str = "mock-llm",
        text: str | None = None,
    ) -> None:
        self._response_text = response_text if response_text is not None else text or ""
        self._model = model

    async def complete(
        self, messages: Sequence[LlmMessage], model: str | None = None
    ) -> LlmResponse:
        return LlmResponse(self._response_text, model or self._model)

    async def stream(
        self, messages: Sequence[LlmMessage], model: str | None = None
    ) -> AsyncIterator[str]:
        for token in self._response_text.split():
            yield token


class OpenRouterLlmProvider:
    def __init__(self, settings: Settings | None = None, client: Any = None) -> None:
        self._settings = settings or get_settings()
        self._client = client or AsyncOpenAI(
            base_url=self._settings.openrouter_base_url,
            api_key=self._settings.openrouter_api_key,
        )

    @staticmethod
    def _serialize_messages(
        messages: Sequence[LlmMessage],
    ) -> list[ChatCompletionMessageParam]:
        return [
            cast(ChatCompletionMessageParam, {"role": message.role, "content": message.content})
            for message in messages
        ]

    def _resolve_model(self, model: str | None) -> str:
        return model or self._settings.default_chat_model

    async def complete(
        self, messages: Sequence[LlmMessage], model: str | None = None
    ) -> LlmResponse:
        response = await self._client.chat.completions.create(
            model=self._resolve_model(model),
            messages=self._serialize_messages(messages),
        )
        text = response.choices[0].message.content or ""
        return LlmResponse(text, response.model)

    async def stream(
        self, messages: Sequence[LlmMessage], model: str | None = None
    ) -> AsyncIterator[str]:
        stream = await self._client.chat.completions.create(
            model=self._resolve_model(model),
            messages=self._serialize_messages(messages),
            stream=True,
        )

        async for chunk in stream:
            token = chunk.choices[0].delta.content
            if token:
                yield token
