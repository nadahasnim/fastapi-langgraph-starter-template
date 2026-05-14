from uuid import uuid4

from app.api.v1.schemas.responses import ResponseObject


class ResponseFormatter:
    def __init__(self, default_model: str) -> None:
        self._default_model = default_model

    def format_text(
        self,
        text: str,
        metadata: dict[str, object] | None = None,
        model: str | None = None,
        response_id: str | None = None,
        extensions: dict[str, object] | None = None,
    ) -> ResponseObject:
        return ResponseObject.create_text_response(
            response_id=response_id or f"resp_{uuid4().hex}",
            model=model or self._default_model,
            text=text,
            metadata=metadata,
            extensions=extensions or {},
        )
