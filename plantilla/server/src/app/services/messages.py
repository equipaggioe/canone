"""The email, the SMS and the push of a request, after the commit.

transport.py says how an email or an SMS goes out; here, when.
"""

import logging
from collections.abc import Awaitable, Callable

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

OUTBOX = "outbox"

type Send = Callable[[], Awaitable[None]]


def later(session: AsyncSession, send: Send) -> None:
    """Send once the request commits: first the evidence."""
    session.info.setdefault(OUTBOX, []).append(send)


async def flush(session: AsyncSession) -> None:
    """Send what the request queued.

    A send that fails goes to the log and does not fail the request: the
    request already committed.
    """
    sends: list[Send] = session.info.pop(OUTBOX, [])
    for send in sends:
        try:
            await send()
        except Exception:
            logger.exception("A message did not go out")
