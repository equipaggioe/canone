"""The push to the apps, by FCM."""

import asyncio
import logging
from collections.abc import MutableMapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from functools import cache
from itertools import batched
from uuid import UUID

import firebase_admin
import sqlalchemy as sa
from firebase_admin import messaging
from google.auth.transport import Request
from google.auth.transport.requests import Request as HttpRequest
from google.oauth2 import service_account
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.account.push_fid import PushFid
from app.schemas.fcm import FidRegistration

logger = logging.getLogger(__name__)

# What send_each_async takes at once.
BATCH = 500
# All that the token of Google allows.
SCOPE = "https://www.googleapis.com/auth/firebase.messaging"


@dataclass(frozen=True)
class Content:
    """What a push shows and opens, and until when."""

    title: str
    body: str
    navigate: str
    channel: str
    ttl: timedelta


@dataclass(frozen=True)
class Installation:
    """Where FCM delivers the pushes of a session."""

    session_id: UUID
    fid: str
    language: str


class Credential(service_account.Credentials):
    """The service account of the deployment.

    Only renew renews its token. send_each_async would do it blocking
    the loop: before each message, and twice for each 401.
    """

    def before_request(
        self, request: Request, method: str, url: str, headers: MutableMapping[str, str]
    ) -> None:
        """Put the token in a message."""
        self.apply(headers)

    # google-auth does not annotate it: pyrefly infers that it never returns.
    def refresh(self, request: Request) -> None:  # pyrefly: ignore[bad-override]
        """Keep the token: the 401 stays the answer of the message."""

    def renew(self) -> None:
        """Get a new token, blocking."""
        super().refresh(HttpRequest())


@cache
def credential() -> Credential:
    """Read the service account of the deployment."""
    return Credential.from_service_account_info(settings.firebase_credentials, scopes=[SCOPE])


@cache
def app() -> firebase_admin.App:
    """Start Firebase with the service account of the deployment."""
    options = {"projectId": settings.firebase_credentials["project_id"]}
    return firebase_admin.initialize_app(credential(), options)


async def register(
    session: AsyncSession, session_id: UUID, body: FidRegistration, language: str
) -> None:
    """Give a session its installation, the one it had replaced.

    The same installation in another session leaves it: the device has
    another session now.
    """
    taken = (PushFid.session_id == session_id) | (PushFid.fid == body.fid)
    await session.execute(sa.delete(PushFid).where(taken))
    row = {"session_id": session_id, "fid": body.fid, "language": language}
    # Of two requests at once with the same one, the first stays.
    await session.execute(insert(PushFid).values(row).on_conflict_do_nothing())


async def find(session: AsyncSession, live: sa.Select[UUID]) -> list[Installation]:
    """Return the installations of the sessions."""
    query = sa.select(PushFid.session_id, PushFid.fid, PushFid.language)
    rows = await session.execute(query.where(PushFid.session_id.in_(live)))
    return [Installation(session_id, fid, language) for session_id, fid, language in rows]


def message(installation: Installation, content: Content) -> messaging.Message:
    """Build the message of an installation."""
    expires = datetime.now(UTC) + content.ttl
    return messaging.Message(
        fid=installation.fid,
        notification=messaging.Notification(title=content.title, body=content.body),
        data={"navigate": content.navigate},
        android=messaging.AndroidConfig(
            ttl=content.ttl,
            notification=messaging.AndroidNotification(channel_id=content.channel),
        ),
        apns=messaging.APNSConfig(headers={"apns-expiration": str(int(expires.timestamp()))}),
    )


async def send(sends: Sequence[tuple[Installation, Content]]) -> list[sa.Delete]:
    """Send each push, and return how to forget who no longer receives.

    The token of Google is renewed first, in a thread.
    """
    firebase = app()
    google = credential()
    if not google.valid:
        await asyncio.to_thread(google.renew)
    gone: list[sa.Delete] = []
    for batch in batched(sends, BATCH, strict=False):
        messages = [message(installation, content) for installation, content in batch]
        answer = await messaging.send_each_async(messages, app=firebase)
        for (installation, _), response in zip(batch, answer.responses, strict=True):
            if isinstance(response.exception, messaging.UnregisteredError):
                gone.append(
                    sa.delete(PushFid).where(
                        PushFid.session_id == installation.session_id,
                        PushFid.fid == installation.fid,
                    )
                )
            elif response.exception is not None:
                logger.error(
                    "A push did not reach the session %s: %s",
                    installation.session_id,
                    type(response.exception).__name__,
                )
    return gone
