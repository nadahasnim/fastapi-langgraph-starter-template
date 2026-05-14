from app.core.config import get_settings


def test_settings_include_database_url(monkeypatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/agent_db"
    )
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.database_url == "postgresql+asyncpg://postgres:postgres@localhost:5432/agent_db"
    get_settings.cache_clear()


def test_settings_include_default_temperature(monkeypatch) -> None:
    monkeypatch.setenv("DEFAULT_TEMPERATURE", "0.35")
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.default_temperature == 0.35
    get_settings.cache_clear()
