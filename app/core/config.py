from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    app_name: str = "agent-backend-template"
    app_debug: bool = True
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/agent_db"
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    default_chat_model: str = "template-chat-model"
    default_temperature: float | None = None
    default_embedding_model: str = "template-embedding-model"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "documents"
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
