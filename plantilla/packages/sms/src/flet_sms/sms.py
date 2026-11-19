"""SMS Retriever on Android, through smart_auth."""

from dataclasses import dataclass
from typing import Optional

import flet as ft
from flet.controls.base_control import control
from flet.controls.services.service import Service


@dataclass
class SmsCodeEvent(ft.Event["SmsCode"]):
    """The code read from the last line of the SMS."""

    code: str


@control("SmsCode")
class SmsCode(Service):
    """Reads the code of the SMS that carries the app's hash, without SMS permissions."""

    on_code: Optional[ft.EventHandler[SmsCodeEvent]] = None

    async def listen(self) -> None:
        """Waits up to five minutes for the next SMS with the app's hash."""
        await self._invoke_method("listen")

    async def stop(self) -> None:
        """Stops waiting for the SMS."""
        await self._invoke_method("stop")

    async def signature(self) -> str:
        """Returns the app's hash, the one the server puts in the SMS."""
        return await self._invoke_method("signature")
