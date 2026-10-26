"""The events of event_log, and what the server may do with them."""

from datetime import UTC, datetime, timedelta

import pytest
import sqlalchemy as sa
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import EventLevel
from app.models.event.event_log import EventLog
from app.services import events


async def insert(session: AsyncSession, occurred_at: datetime) -> None:
    """Insert an event at a given time."""
    row = events.event("authn_login_fail", EventLevel.WARN)
    row.occurred_at = occurred_at
    session.add(row)
    await session.flush()


async def in_savepoint(session: AsyncSession, statement: str) -> None:
    """Run a statement in a savepoint, which a refusal rolls back."""
    async with session.begin_nested():
        await session.execute(sa.text(statement))


async def test_server_inserts_and_reads_events(session: AsyncSession) -> None:
    """The role of the server inserts an event and reads it back."""
    await in_savepoint(
        session,
        "INSERT INTO event_log (action, level, trace_id) VALUES ('authn_login_fail', 'warn', '')",
    )
    await in_savepoint(session, "SELECT * FROM event_log")


@pytest.mark.parametrize(
    "statement",
    ["UPDATE event_log SET level = 'info'", "DELETE FROM event_log", "TRUNCATE event_log"],
)
async def test_server_cannot_change_events(session: AsyncSession, statement: str) -> None:
    """The role of the server neither changes nor deletes the trail."""
    with pytest.raises(DBAPIError, match="permission denied"):
        await in_savepoint(session, statement)


async def test_purge_deletes_only_expired_events(session: AsyncSession, owner: None) -> None:
    """The purge keeps what is in retention."""
    now = datetime.now(UTC)
    await insert(session, now - timedelta(days=events.RETENTION_DAYS + 1))
    await insert(session, now)
    await events.purge()
    left = await session.scalars(sa.select(EventLog.occurred_at))
    assert list(left) == [now]


async def test_record_writes_the_event(session: AsyncSession) -> None:
    """An event recorded alone opens and commits its own transaction."""
    await events.record(events.event("authz_fail", EventLevel.CRITICAL))
    action = await session.scalar(sa.select(EventLog.action))
    assert action == "authz_fail"


def test_changes_keep_only_listed_values(monkeypatch: pytest.MonkeyPatch) -> None:
    """A field off the list is logged as changed, without its value."""
    monkeypatch.setitem(events.LOGGED_FIELDS, "account", frozenset({"role"}))
    logged = events.changes("account", {"role": "admin", "email": "a@example.com"})
    assert logged == {"changed": ["email", "role"], "values": {"role": "admin"}}
