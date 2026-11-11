"""The health check, and what to alert on."""

import os
import shutil
from datetime import UTC, datetime
from pathlib import Path

import pytest
import sqlalchemy as sa
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession
from valkey.asyncio import Valkey

from app import store
from app.config import settings
from app.database import engine
from app.enums import EventLevel
from app.models.event.event_log import EventLog
from app.services import events


@pytest.fixture
def app_folder(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point STATE_DIRECTORY to files/ inside a folder of the app."""
    (tmp_path / "files").mkdir()
    monkeypatch.setenv("STATE_DIRECTORY", str(tmp_path / "files"))
    return tmp_path


@pytest.mark.parametrize("path", ["/api/health/events", "/api/health/event-log"])
@pytest.mark.parametrize("headers", [{}, {"Authorization": "Bearer wrong"}])
async def test_events_need_the_token(
    client: AsyncClient, app_folder: Path, path: str, headers: dict[str, str]
) -> None:
    """Without the token, the routes answer 401."""
    response = await client.get(path, headers=headers)
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


async def test_events_tell_last_critical_and_backup(
    client: AsyncClient, session: AsyncSession, app_folder: Path
) -> None:
    """The route answers the last critical event and the last backup."""
    headers = {"Authorization": f"Bearer {settings.health_token}"}
    response = await client.get("/api/health/events", headers=headers)
    first = response.json()
    assert (first["lastCriticalAt"], first["lastBackupAt"]) == (None, None)
    row = events.event("authz_admin", EventLevel.CRITICAL)
    session.add(row)
    await session.flush()
    await session.refresh(row)
    backup = app_folder / "last-backup"
    backup.write_bytes(b"")
    os.utime(backup, (1_800_000_000, 1_800_000_000))
    body = (await client.get("/api/health/events", headers=headers)).json()
    assert datetime.fromisoformat(body["lastCriticalAt"]) == row.occurred_at
    assert datetime.fromisoformat(body["lastBackupAt"]) == datetime.fromtimestamp(
        1_800_000_000, UTC
    )


async def test_events_tell_the_last_event(
    client: AsyncClient, session: AsyncSession, app_folder: Path
) -> None:
    """The route answers the last event of any level."""
    headers = {"Authorization": f"Bearer {settings.health_token}"}
    first = (await client.get("/api/health/events", headers=headers)).json()
    assert first["lastEventAt"] is None
    row = events.event("authn_login_success", EventLevel.INFO)
    session.add(row)
    await session.flush()
    await session.refresh(row)
    body = (await client.get("/api/health/events", headers=headers)).json()
    assert datetime.fromisoformat(body["lastEventAt"]) == row.occurred_at
    assert body["lastCriticalAt"] is None


async def test_events_tell_the_disk(client: AsyncClient, app_folder: Path) -> None:
    """The route answers the free and total bytes of the disk."""
    headers = {"Authorization": f"Bearer {settings.health_token}"}
    body = (await client.get("/api/health/events", headers=headers)).json()
    usage = shutil.disk_usage(app_folder)
    assert body["diskTotalBytes"] == usage.total
    assert 0 <= body["diskFreeBytes"] <= usage.total


async def insert_event(connection: AsyncConnection) -> int:
    """Insert an event as the server and return its id."""
    statement = (
        sa.insert(EventLog)
        .values(action="authn_login_fail", level=EventLevel.WARN, trace_id="")
        .returning(EventLog.id)
    )
    return (await connection.execute(statement)).scalar_one()


async def read_event_log(client: AsyncClient) -> list[int]:
    """Read the event log one event per page, to the last page."""
    headers = {"Authorization": f"Bearer {settings.health_token}"}
    ids: list[int] = []
    token = ""
    while True:
        params = {"pageSize": 1, "pageToken": token}
        body = (await client.get("/api/health/event-log", headers=headers, params=params)).json()
        ids += [item["id"] for item in body["items"]]
        token = body["nextPageToken"]
        if not token:
            return ids


async def test_event_log_waits_for_an_open_transaction(
    client: AsyncClient, committed: list[int]
) -> None:
    """An event that commits late holds back the events after it."""
    async with engine.connect() as late:
        transaction = await late.begin()
        committed.append(await insert_event(late))
        async with engine.begin() as other:
            committed.append(await insert_event(other))
        assert await read_event_log(client) == []
        await transaction.commit()
    assert await read_event_log(client) == committed


async def test_health_answers_with_its_dependencies(client: AsyncClient) -> None:
    """The check answers 204 while the database and Valkey answer."""
    assert (await client.get("/api/health")).status_code == 204


async def test_health_needs_valkey(client: AsyncClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """Without Valkey the check answers 503, though the process does."""
    unreachable = Valkey.from_url("valkey://127.0.0.1:1/0")
    monkeypatch.setattr(store, "client", unreachable)
    try:
        assert (await client.get("/api/health")).status_code == 503
    finally:
        await unreachable.aclose()


async def test_wrong_token_is_an_event(
    client: AsyncClient, session: AsyncSession, app_folder: Path
) -> None:
    """A request without the token leaves authn_login_fail."""
    await client.get("/api/health/events", headers={"Authorization": "Bearer wrong"})
    assert await session.scalar(sa.select(EventLog.action)) == "authn_login_fail"
