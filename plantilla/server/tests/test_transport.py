"""The email and the SMS go to the API of Equipaggio, with the key."""

import json
import re
from datetime import UTC, datetime, timedelta

import httpx

from app.config import settings
from app.services import transport

EXPIRES = datetime(2030, 1, 1, tzinfo=UTC)


def to_equipaggio(request: httpx.Request, kind: str) -> dict[str, object]:
    """Check a PUT of a new id to the API with the key, and read it."""
    assert request.method == "PUT"
    assert re.fullmatch(rf"/api/{kind}/[0-9a-f-]{{36}}", request.url.path)
    assert request.url.host == "equipaggio.net"
    assert request.headers["authorization"] == f"Bearer {settings.equipaggio_key}"
    found: dict[str, object] = json.loads(request.content)
    return found


async def test_email_goes_to_the_api_of_equipaggio(sent: list[httpx.Request]) -> None:
    """With its text, its HTML and when it expires."""
    await transport.email("bea@example.com", "Asunto", "Texto", "<p>Texto</p>", EXPIRES)
    (request,) = sent
    assert to_equipaggio(request, "email") == {
        "to": "bea@example.com",
        "subject": "Asunto",
        "text": "Texto",
        "html": "<p>Texto</p>",
        "attachments": [],
        "expiresAt": EXPIRES.isoformat(),
    }


async def test_sms_goes_to_the_api_of_equipaggio(sent: list[httpx.Request]) -> None:
    """With its text and when it expires."""
    await transport.sms("+56221234567", "Hola", EXPIRES + timedelta(minutes=1))
    (request,) = sent
    assert to_equipaggio(request, "sms") == {
        "to": "+56221234567",
        "body": "Hola",
        "expiresAt": (EXPIRES + timedelta(minutes=1)).isoformat(),
    }
