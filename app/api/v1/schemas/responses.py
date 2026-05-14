from typing import Any, Literal

from pydantic import BaseModel, Field


class ResponseCreateRequest(BaseModel):
    input: str = Field(min_length=1)
    model: str | None = None
    conversation_id: str | None = None
    stream: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class ResponseContent(BaseModel):
    type: Literal["output_text"] = "output_text"
    text: str


class ResponseMessage(BaseModel):
    type: Literal["message"] = "message"
    role: Literal["assistant"] = "assistant"
    content: list[ResponseContent]


class ResponseUsage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class ResponseObject(BaseModel):
    id: str
    object: Literal["response"] = "response"
    model: str
    output: list[ResponseMessage]
    usage: ResponseUsage = Field(default_factory=ResponseUsage)
    metadata: dict[str, Any] = Field(default_factory=dict)
    extensions: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_text_response(
        cls,
        response_id: str,
        model: str,
        text: str,
        metadata: dict[str, Any] | None = None,
        extensions: dict[str, Any] | None = None,
    ) -> "ResponseObject":
        return cls(
            id=response_id,
            model=model,
            output=[ResponseMessage(content=[ResponseContent(text=text)])],
            metadata=metadata or {},
            extensions=extensions or {},
        )
