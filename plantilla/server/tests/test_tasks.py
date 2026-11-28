"""The tasks of the machine."""

import asyncio
import os
import signal
import time
from pathlib import Path
from uuid import UUID

import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app import database, tasks, tracing
from app.services import files, web_push


async def test_sweep_deletes_only_old_files_without_row(
    session: AsyncSession, owner: None, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A file with a row, or newer than the margin, stays.

    The owner creates the table, as a migration would.
    """
    table = sa.Table("note_file", sa.MetaData(), sa.Column("id", sa.Uuid, primary_key=True))
    await session.run_sync(lambda sync: table.create(sync.connection()))
    kept = "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
    await session.execute(table.insert().values(id=UUID(kept)))
    monkeypatch.setattr(files, "file_tables", lambda: [table])
    monkeypatch.setenv("STATE_DIRECTORY", str(tmp_path))
    folder = tmp_path
    past = time.time() - files.MARGIN_SECONDS - 60
    for name in (kept, "orphan", "recent"):
        (folder / name).write_bytes(b"")
    # An image in sizes is a folder with the id of its row.
    (folder / "orphan-sizes").mkdir()
    (folder / "orphan-sizes" / "thumb.webp").write_bytes(b"")
    for name in (kept, "orphan", "orphan-sizes"):
        os.utime(folder / name, (past, past))
    await files.sweep()
    assert sorted(path.name for path in folder.iterdir()) == [kept, "recent"]


def test_seeders_run_by_module_and_name(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Only the seed_ coroutines a module defines count, by name."""
    package = tmp_path / "fake_seeders"
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "b_places.py").write_text("async def seed_places(session): ...\n", encoding="utf-8")
    (package / "a_roles.py").write_text(
        "from fake_seeders.b_places import seed_places\n"
        "async def seed_users(session): ...\n"
        "async def seed_roles(session): ...\n"
        "def seed_sync(session): ...\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    found = [
        f"{seeder.__module__}.{seeder.__name__}" for seeder in database.seeders("fake_seeders")
    ]
    assert found == [
        "fake_seeders.a_roles.seed_roles",
        "fake_seeders.a_roles.seed_users",
        "fake_seeders.b_places.seed_places",
    ]


def stop() -> None:
    """Send SIGTERM to the process, as systemd stops a worker."""
    signal.raise_signal(signal.SIGTERM)


async def test_worker_runs_after_a_failed_round(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """A failed round goes to the log, and the next one runs."""
    rounds = 0

    async def flaky() -> None:
        nonlocal rounds
        rounds += 1
        if rounds == 1:
            raise RuntimeError("the first round fails")
        if rounds == 3:
            stop()

    monkeypatch.setitem(tasks.TASKS, "flaky", flaky)
    monkeypatch.setitem(tasks.WORKERS, "flaky", 0)
    await asyncio.wait_for(tasks.work("flaky"), 5)
    assert rounds == 3
    assert "the first round fails" in caplog.text


async def test_worker_ends_its_round_on_sigterm(monkeypatch: pytest.MonkeyPatch) -> None:
    """SIGTERM lets the round end, and no other starts."""
    rounds: list[str] = []

    async def slow() -> None:
        rounds.append("started")
        stop()
        await asyncio.sleep(0.05)
        rounds.append("ended")

    monkeypatch.setitem(tasks.TASKS, "slow", slow)
    monkeypatch.setitem(tasks.WORKERS, "slow", 3600)
    await asyncio.wait_for(tasks.work("slow"), 5)
    assert rounds == ["started", "ended"]


class Idle:
    """A pool and a client that close nothing."""

    async def dispose(self) -> None:
        """Keep the pool of the tests."""

    async def aclose(self) -> None:
        """Keep the connections of the tests."""


async def test_each_round_has_its_own_trace(monkeypatch: pytest.MonkeyPatch) -> None:
    """A task and each round of a worker start a trace."""
    traces: list[str] = []

    async def probe() -> None:
        traces.append(tracing.trace_id())
        if len(traces) == 2:
            stop()

    monkeypatch.setitem(tasks.TASKS, "probe", probe)
    monkeypatch.setitem(tasks.WORKERS, "probe", 0)
    await asyncio.wait_for(tasks.work("probe"), 5)
    monkeypatch.delitem(tasks.WORKERS, "probe")
    monkeypatch.setattr(tasks, "engine", Idle())
    monkeypatch.setattr(web_push, "client", Idle())
    await tasks.run("probe")
    assert "" not in traces
    assert len(set(traces)) == 3
