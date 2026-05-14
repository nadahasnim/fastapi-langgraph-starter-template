from app.core.config import get_settings


def test_settings_include_database_url(monkeypatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/agent_db"
    )
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.database_url == "postgresql+asyncpg://postgres:postgres@localhost:5432/agent_db"
    get_settings.cache_clear()
