"""The email and the SMS, by the API of Equipaggio, after the commit."""

import logging
from collections.abc import Awaitable, Callable
from datetime import datetime
from uuid import uuid4

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings

logger = logging.getLogger(__name__)

# README.md, «Instrumentos»: the API of Equipaggio is the same for every
# deployment; the key of each one is in Settings.
API = "https://equipaggio.net/api"
OUTBOX = "outbox"

type Send = Callable[[], Awaitable[None]]

client = httpx.AsyncClient(
    base_url=API, headers={"Authorization": f"Bearer {settings.equipaggio_key}"}
)


async def email(to: str, subject: str, text: str, html: str, expires: datetime) -> None:
    """Queue an email in Equipaggio, with its text and its HTML."""
    body: dict[str, object] = {
        "to": to,
        "subject": subject,
        "text": text,
        "html": html,
        "attachments": [],
        "expiresAt": expires.isoformat(),
    }
    response = await client.put(f"/email/{uuid4()}", json=body)
    response.raise_for_status()


async def sms(to: str, text: str, expires: datetime) -> None:
    """Queue an SMS in Equipaggio."""
    body = {"to": to, "body": text, "expiresAt": expires.isoformat()}
    response = await client.put(f"/sms/{uuid4()}", json=body)
    response.raise_for_status()


def later(session: AsyncSession, send: Send) -> None:
    """Send once the request commits: first the evidence."""
    session.info.setdefault(OUTBOX, []).append(send)


async def flush(session: AsyncSession) -> None:
    """Send what the request queued.

    A send that fails goes to the log and does not fail the request.
    """
    sends: list[Send] = session.info.pop(OUTBOX, [])
    for send in sends:
        try:
            await send()
        except httpx.HTTPError:
            logger.exception("A message did not reach Equipaggio")
