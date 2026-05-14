"""Observability wrapper for optional Langfuse tracing."""

from contextlib import contextmanager
from typing import Any

from langfuse import Langfuse


class NoopTrace:
    """No-op trace implementation when observability is disabled."""

    def update(self, **kwargs: Any) -> None:
        """No-op update."""
        pass

    def end(self, **kwargs: Any) -> None:
        """No-op end."""
        pass


class LangfuseTrace:
    """Langfuse trace wrapper."""

    def __init__(self, observation: Any) -> None:
        self._observation = observation

    def update(self, **kwargs: Any) -> None:
        """Update observation with metadata."""
        self._observation.update(**kwargs)

    def end(self, **kwargs: Any) -> None:
        """End observation."""
        self._observation.end(**kwargs)


class Observability:
    """Observability wrapper that safely handles missing credentials."""

    def __init__(
        self,
        enabled: bool = False,
        public_key: str | None = None,
        secret_key: str | None = None,
        host: str | None = None,
    ) -> None:
        self.enabled = enabled
        self._client: Langfuse | None = None

        if enabled and public_key and secret_key:
            self._client = Langfuse(
                public_key=public_key,
                secret_key=secret_key,
                host=host or "https://cloud.langfuse.com",
            )

    def start_trace(self, name: str, metadata: dict[str, Any] | None = None) -> NoopTrace | LangfuseTrace:
        """Start a new observation without setting it as current context."""
        if not self._client:
            return NoopTrace()

        observation = self._client.start_observation(
            name=name,
            as_type="span",
            metadata=metadata or {},
        )
        return LangfuseTrace(observation)

    @contextmanager
    def trace(self, name: str, metadata: dict[str, Any] | None = None):
        """Context manager for tracing with automatic cleanup."""
        if not self._client:
            yield NoopTrace()
            return

        with self._client.start_as_current_observation(
            name=name,
            as_type="span",
            metadata=metadata or {},
        ) as observation:
            yield LangfuseTrace(observation)
