"""The client of Valkey, one for the app."""

from valkey.asyncio import Valkey

from app.config import settings

client = Valkey.from_url(settings.valkey_url)
