"""The health check, and what to alert on."""

import os
from datetime import UTC, datetime
from pathlib import Path

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.enums import EventLevel
from app.services import events


@pytest.fixture
def app_folder(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point STATE_DIRECTORY to files/ inside a folder of the app."""
    (tmp_path / "files").mkdir()
    monkeypatch.setenv("STATE_DIRECTORY", str(tmp_path / "files"))
    return tmp_path


@pytest.mark.parametrize("headers", [{}, {"Authorization": "Bearer wrong"}])
async def test_events_need_the_token(
    client: AsyncClient, app_folder: Path, headers: dict[str, str]
) -> None:
    """Without the token, the route answers 401."""
    response = await client.get("/api/health/events", headers=headers)
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


async def test_events_tell_last_critical_and_backup(
    client: AsyncClient, session: AsyncSession, app_folder: Path
) -> None:
    """The route answers the last critical event and the last backup."""
    headers = {"Authorization": f"Bearer {settings.health_token}"}
    response = await client.get("/api/health/events", headers=headers)
    assert response.json() == {"lastCriticalAt": None, "lastBackupAt": None}
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
