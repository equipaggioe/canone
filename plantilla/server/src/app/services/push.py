"""The push to every device of an account, after the commit."""

import asyncio
import logging
from collections.abc import Callable, Coroutine
from datetime import UTC, datetime, timedelta
from functools import partial
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app import push
from app.database import SessionFactory
from app.enums import Push
from app.models.account.account_session import AccountSession
from app.services import fcm, messages, sessions, web_push
from app.services.fcm import Content

logger = logging.getLogger(__name__)

# fastapi.md: what a push waits for its service.
WAIT = timedelta(seconds=5)

type Render = Callable[[str], Content]


async def later(session: AsyncSession, account_id: UUID, render: Render) -> None:
    """Push to every live session once the request commits.

    The devices are read now: the request may end their sessions.
    """
    live = sa.select(AccountSession.id).where(
        AccountSession.account_id == account_id,
        AccountSession.last_used_at > datetime.now(UTC) - sessions.IDLE,
    )
    installations = await fcm.find(session, live) if Push.FCM in push.PUSH else []
    subscriptions = await web_push.find(session, live) if Push.WEB in push.PUSH else []
    if installations or subscriptions:
        found = partial(send, installations, subscriptions, render)
        messages.later(session, found)


async def within(sending: Coroutine[None, None, list[sa.Delete]], who: str) -> list[sa.Delete]:
    """Wait for a push at most WAIT; a failure goes to the log.

    The log takes the type of the error: its text may have an endpoint.
    """
    try:
        async with asyncio.timeout(WAIT.total_seconds()):
            return await sending
    except Exception as error:
        logger.error("A push did not reach %s: %s", who, type(error).__name__)
        return []


async def send(
    installations: list[fcm.Installation],
    subscriptions: list[web_push.Subscription],
    render: Render,
) -> None:
    """Send every push at once, and forget who no longer receives."""
    sending = [
        within(web_push.send(to, render(to.language)), f"the session {to.session_id}")
        for to in subscriptions
    ]
    if installations:
        sends = [(to, render(to.language)) for to in installations]
        sending.append(within(fcm.send(sends), "FCM"))
    gone = [statement for found in await asyncio.gather(*sending) for statement in found]
    if gone:
        async with SessionFactory.begin() as session:
            for statement in gone:
                await session.execute(statement)
