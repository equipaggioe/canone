"""How the email and the SMS leave: by the API of Equipaggio.

fastapi.md, «Correo y SMS»: each repository declares here how they go
out; messages.py decides when.
"""

from datetime import datetime
from uuid import uuid4

import httpx

from app.config import settings

# README.md, «Instrumentos»: the API of Equipaggio is the same for every
# deployment; the key of each one is in Settings.
API = "https://equipaggio.net/api"

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
