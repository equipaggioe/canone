"""Settings read from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Every field is required and has no default."""

    database_url: str
    min_client_versions: dict[str, str]


settings = Settings()
