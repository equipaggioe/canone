"""The push to the browsers, by Web Push."""

import base64
import json
import logging
import socket
import time
from dataclasses import dataclass
from datetime import timedelta
from http import HTTPStatus
from ipaddress import ip_address
from urllib.parse import urlsplit
from uuid import UUID

import aiohttp
import sqlalchemy as sa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from py_vapid import Vapid02
from pywebpush import WebPusher
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.account.push_subscription import PushSubscription
from app.schemas.web_push import SubscriptionRegistration, decode
from app.services.fcm import Content

logger = logging.getLogger(__name__)

# RFC 8292: the JWT lasts 24 hours at most.
JWT_LIFETIME = timedelta(hours=12)
# What a push service answers to a subscription that is no more.
GONE = (HTTPStatus.NOT_FOUND, HTTPStatus.GONE)

private_key = ec.derive_private_key(int.from_bytes(decode(settings.vapid_key)), ec.SECP256R1())
vapid = Vapid02(private_key)
PUBLIC_KEY = (
    base64.urlsafe_b64encode(
        private_key.public_key().public_bytes(
            serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint
        )
    )
    .rstrip(b"=")
    .decode()
)


@dataclass(frozen=True)
class Subscription:
    """Where a push service delivers the pushes of a session."""

    session_id: UUID
    endpoint: str
    p256dh: str
    auth: str
    language: str


def is_global(host: str) -> bool:
    """Tell whether an address is of the public Internet."""
    return ip_address(host).is_global


def open_socket(info: aiohttp.AddrInfoType) -> socket.socket:
    """Open the socket of an address, if it is global.

    The client chooses the endpoint: it must not take the server to its
    own network.
    """
    family, kind, protocol, _, address = info
    if not is_global(str(address[0])):
        raise OSError("The address is not global")
    return socket.socket(family, kind, protocol)


class Client:
    """The aiohttp session of the process, opened on its first use."""

    def __init__(self) -> None:
        """Start without a session: it belongs to a running loop."""
        self.http: aiohttp.ClientSession | None = None

    async def post(self, url: str, headers: dict[str, str], body: bytes) -> int:
        """Post a push, and return the status.

        It follows no redirection, reads no body and keeps no cookie.
        """
        if self.http is None:
            connector = aiohttp.TCPConnector(socket_factory=open_socket)
            self.http = aiohttp.ClientSession(
                connector=connector, cookie_jar=aiohttp.DummyCookieJar()
            )
        async with self.http.post(
            url, data=body, headers=headers, allow_redirects=False
        ) as response:
            return response.status

    async def aclose(self) -> None:
        """Close the session, if it opened."""
        if self.http is not None:
            await self.http.close()
            self.http = None


client = Client()


async def register(
    session: AsyncSession, session_id: UUID, body: SubscriptionRegistration, language: str
) -> None:
    """Give a session its subscription, the one it had replaced.

    The same subscription in another session leaves it: the browser has
    another session now.
    """
    taken = (PushSubscription.session_id == session_id) | (
        PushSubscription.endpoint == body.endpoint
    )
    await session.execute(sa.delete(PushSubscription).where(taken))
    row = {
        "session_id": session_id,
        "endpoint": body.endpoint,
        "p256dh": body.keys.p256dh,
        "auth": body.keys.auth,
        "language": language,
    }
    # Of two requests at once with the same one, the first stays.
    await session.execute(insert(PushSubscription).values(row).on_conflict_do_nothing())


async def find(session: AsyncSession, live: sa.Select[UUID]) -> list[Subscription]:
    """Return the subscriptions of the sessions."""
    query = sa.select(
        PushSubscription.session_id,
        PushSubscription.endpoint,
        PushSubscription.p256dh,
        PushSubscription.auth,
        PushSubscription.language,
    )
    rows = await session.execute(query.where(PushSubscription.session_id.in_(live)))
    return [
        Subscription(session_id, endpoint, p256dh, auth, language)
        for session_id, endpoint, p256dh, auth, language in rows
    ]


def declarative(content: Content) -> bytes:
    """Write a push as a declarative message."""
    notification = {"title": content.title, "body": content.body, "navigate": content.navigate}
    document = {"web_push": 8030, "notification": notification}
    return json.dumps(document, ensure_ascii=False).encode()


async def send(subscription: Subscription, content: Content) -> list[sa.Delete]:
    """Send a push, and return how to forget who no longer receives."""
    keys = {"p256dh": subscription.p256dh, "auth": subscription.auth}
    pusher = WebPusher({"endpoint": subscription.endpoint, "keys": keys})
    body = pusher.encode(declarative(content))["body"]
    parts = urlsplit(subscription.endpoint)
    claims = {
        "aud": f"{parts.scheme}://{parts.netloc}",
        "exp": int(time.time() + JWT_LIFETIME.total_seconds()),
        "sub": f"mailto:{settings.contact}",
    }
    headers = {
        "Content-Encoding": "aes128gcm",
        "TTL": str(int(content.ttl.total_seconds())),
        **vapid.sign(claims),
    }
    status = await client.post(subscription.endpoint, headers, body)
    if status in GONE:
        return [
            sa.delete(PushSubscription).where(
                PushSubscription.session_id == subscription.session_id,
                PushSubscription.endpoint == subscription.endpoint,
            )
        ]
    if not 200 <= status < 300:
        logger.error("A push did not reach the session %s: %d", subscription.session_id, status)
    return []
