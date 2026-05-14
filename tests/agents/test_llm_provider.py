from typing import Any, cast

import pytest

from app.agents.shared.llm import LlmMessage, MockLlmProvider, OpenRouterLlmProvider


@pytest.mark.asyncio
async def test_mock_llm_provider_complete_returns_configured_text_and_model() -> None:
    provider = MockLlmProvider(response_text="configured response", model="mock-model")

    response = await provider.complete([], model="passed-model")

    assert response.text == "configured response"
    assert response.model == "passed-model"


@pytest.mark.asyncio
async def test_mock_llm_provider_stream_yields_token_chunks_for_hello_world() -> None:
    provider = MockLlmProvider(response_text="hello world")

    chunks = [chunk async for chunk in provider.stream([], model="passed-model")]

    assert chunks == ["hello", "world"]


class _StubCompletions:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    async def create(self, **kwargs: object):
        self.calls.append(kwargs)
        if kwargs.get("stream"):
            return _StubStream(["hello", None, "world"])
        return type(
            "_Response",
            (),
            {
                "choices": [
                    type(
                        "_Choice",
                        (),
                        {"message": type("_Message", (), {"content": "stub completion"})()},
                    )()
                ],
                "model": "stub-response-model",
            },
        )()


class _StubStream:
    def __init__(self, chunks: list[str | None]) -> None:
        self._chunks = chunks

    def __aiter__(self):
        return self._iterate()

    async def _iterate(self):
        for chunk in self._chunks:
            yield type(
                "_Chunk",
                (),
                {
                    "choices": [
                        type(
                            "_Choice",
                            (),
                            {"delta": type("_Delta", (), {"content": chunk})()},
                        )()
                    ]
                },
            )()


class _StubClient:
    def __init__(self) -> None:
        self.chat = type(
            "_Chat",
            (),
            {"completions": _StubCompletions()},
        )()


@pytest.mark.asyncio
async def test_openrouter_llm_provider_complete_uses_passed_model_and_serializes_messages() -> None:
    settings = type(
        "_Settings",
        (),
        {
            "openrouter_base_url": "https://example.test",
            "openrouter_api_key": "test-key",
            "default_chat_model": "default-model",
        },
    )()
    client = _StubClient()
    provider = OpenRouterLlmProvider(settings=cast(Any, settings), client=client)

    response = await provider.complete(
        [LlmMessage(role="user", content="hello")],
        model="override-model",
    )

    assert response.text == "stub completion"
    assert response.model == "stub-response-model"
    assert cast(Any, client.chat).completions.calls == [
        {
            "model": "override-model",
            "messages": [{"role": "user", "content": "hello"}],
        }
    ]


@pytest.mark.asyncio
async def test_openrouter_llm_provider_stream_uses_passed_model_and_yields_chunks() -> None:
    settings = type(
        "_Settings",
        (),
        {
            "openrouter_base_url": "https://example.test",
            "openrouter_api_key": "test-key",
            "default_chat_model": "default-model",
        },
    )()
    client = _StubClient()
    provider = OpenRouterLlmProvider(settings=cast(Any, settings), client=client)

    chunks = [
        chunk
        async for chunk in provider.stream(
            [LlmMessage(role="user", content="hello")],
            model="override-model",
        )
    ]

    assert chunks == ["hello", "world"]
    assert cast(Any, client.chat).completions.calls == [
        {
            "model": "override-model",
            "messages": [{"role": "user", "content": "hello"}],
            "stream": True,
        }
    ]
