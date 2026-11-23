"""Credential Manager on Android and AuthenticationServices on iOS."""

from flet.controls.base_control import control
from flet.controls.services.service import Service


@control("Passkey")
class Passkey(Service):
    """Runs a WebAuthn ceremony with the passkeys of the system.

    The options and the response are the JSON of WebAuthn, as the server
    sends and reads them.
    """

    async def get(self, options: str) -> str:
        """Signs in: options of navigator.credentials.get()."""
        return await self._invoke_method("get", {"options": options})

    async def create(self, options: str) -> str:
        """Creates a passkey: options of navigator.credentials.create()."""
        return await self._invoke_method("create", {"options": options})
