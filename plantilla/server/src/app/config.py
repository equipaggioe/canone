"""Settings read from the credentials of the systemd unit."""

import os
from typing import Annotated

from pydantic import StringConstraints
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

VERSION = r"[0-9]+\.[0-9]+\.[0-9]+"


class Settings(BaseSettings):
    """Every field is required and has no default."""

    # ADR-0070: the units load the credentials folder with this prefix.
    model_config = SettingsConfigDict(env_prefix="app_")

    database_url: str
    min_client_versions: dict[str, Annotated[str, StringConstraints(pattern=f"^{VERSION}$")]]
    page_token_key: str

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Read only the credentials: a value comes from one place."""
        return (file_secret_settings,)


settings = Settings(_secrets_dir=os.environ["CREDENTIALS_DIRECTORY"])
