"""Settings read from environment variables."""

from typing import Annotated

from pydantic import StringConstraints
from pydantic_settings import BaseSettings

VERSION = r"[0-9]+\.[0-9]+\.[0-9]+"


class Settings(BaseSettings):
    """Every field is required and has no default."""

    database_url: str
    min_client_versions: dict[str, Annotated[str, StringConstraints(pattern=f"^{VERSION}$")]]
    page_token_key: str


settings = Settings()
