from typing import Any, Literal

from pydantic import BaseModel, Field


class DocumentObject(BaseModel):
    id: str
    object: Literal["document"] = "document"
    user_id: str
    filename: str
    content_type: str
    source: str
    chunk_count: int
    created_at: str
    metadata: dict[str, Any] = Field(default_factory=dict)
