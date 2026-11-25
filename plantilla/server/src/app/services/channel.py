"""What reaches the WebSockets of an account, in its Valkey channel."""

import json
import logging
from collections.abc import Iterable
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from valkey.exceptions import ValkeyError

from app import store
from app.schemas.base import Schema

logger = logging.getLogger(__name__)

OUTBOX = "channel"


def name(account_id: UUID) -> str:
    """Name the channel of an account."""
    return f"account:{account_id}"


def later(session: AsyncSession, account_id: UUID, payload: dict[str, Any]) -> None:
    """Publish once the request commits."""
    session.info.setdefault(OUTBOX, []).append((name(account_id), json.dumps(payload)))


def close(session: AsyncSession, account_id: UUID, session_ids: Iterable[UUID]) -> None:
    """Close the connections of the sessions that ended."""
    ended = [str(session_id) for session_id in session_ids]
    if ended:
        later(session, account_id, {"close": ended})


def send(session: AsyncSession, account_id: UUID, message: Schema) -> None:
    """Send a message to every connection of an account."""
    later(session, account_id, {"message": message.model_dump(mode="json")})


async def flush(session: AsyncSession) -> None:
    """Publish what the request queued.

    A process that cannot reach Valkey loses its subscription too, and
    closes its connections.
    """
    for channel, payload in session.info.pop(OUTBOX, []):
        try:
            await store.client.publish(channel, payload)
        except (ValkeyError, OSError):
            logger.exception("A message did not reach its channel")
