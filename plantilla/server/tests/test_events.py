"""The events of event_log, and what the server may do with them."""

from datetime import UTC, datetime, timedelta

import pytest
import sqlalchemy as sa
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app import errors, main
from app.enums import EventLevel
from app.models.event.event_log import EventLog
from app.schemas.base import InputSchema
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


async def test_only_the_server_and_owner_read_events(session: AsyncSession) -> None:
    """No other role reads event_log, by a grant or a membership."""
    grants = sa.text(
        "SELECT DISTINCT pg_get_userbyid(a.grantee) FROM pg_class c, aclexplode(c.relacl) a "
        "WHERE c.oid = 'event_log'::regclass AND a.privilege_type = 'SELECT'"
    )
    expected = sa.text(
        "SELECT current_user UNION SELECT pg_get_userbyid(relowner) "
        "FROM pg_class WHERE oid = 'event_log'::regclass"
    )
    members = sa.text(
        "SELECT count(*) FROM pg_auth_members WHERE roleid IN "
        "(SELECT oid FROM pg_roles WHERE rolname IN (:server, :owner))"
    )
    readers = set(await session.scalars(grants))
    server, owner = sorted(await session.scalars(expected), key=len)
    assert readers == {server, owner}
    assert await session.scalar(members, {"server": server, "owner": owner}) == 0


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


def test_malformed_address_is_left_out() -> None:
    """An address that is not one is named in details, not stored."""
    row = events.event("authn_login_fail", EventLevel.WARN, ip_address="not-an-ip")
    assert row.ip_address is None
    assert row.details == {"malformed": ["ip_address"]}


class Item(InputSchema):
    """A body with a field and a value from a list."""

    level: EventLevel


@pytest.mark.parametrize(
    ("body", "action"),
    [
        ({}, "input_validation_fail"),
        ({"level": "loud"}, "input_validation_discrete_fail"),
        ({"level": "info", "color": "red"}, "malicious_extraneous"),
    ],
)
async def test_validation_error_is_an_event(
    session: AsyncSession, body: dict[str, str], action: str
) -> None:
    """Each 422 leaves its event of the OWASP vocabulary."""
    probe = FastAPI()
    errors.install(probe)

    @probe.post("/items")
    async def create_item(item: Item) -> None:
        """Accept an item."""

    transport = ASGITransport(app=probe)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/items", json=body)
    assert response.status_code == 422
    assert await session.scalar(sa.select(EventLog.action)) == action


class Pool:
    """A pool of connections that the test keeps."""

    async def dispose(self) -> None:
        """Keep the connection of the test, as an engine."""

    async def aclose(self) -> None:
        """Keep the connections of the test, as a Valkey client."""


async def test_lifespan_logs_start_and_stop(
    session: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The app logs when it starts and when it stops."""
    monkeypatch.setattr(main, "engine", Pool())
    monkeypatch.setattr(main.store, "client", Pool())
    async with main.lifespan(main.app):
        pass
    actions = await session.scalars(sa.select(EventLog.action).order_by(EventLog.id))
    assert list(actions) == ["sys_startup", "sys_shutdown"]
