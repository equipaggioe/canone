"""The tasks of the machine."""

import os
import time
from pathlib import Path
from uuid import UUID

import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app import tasks
from app.services import files


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
    for name in (kept, "orphan"):
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
    found = [f"{seeder.__module__}.{seeder.__name__}" for seeder in tasks.seeders("fake_seeders")]
    assert found == [
        "fake_seeders.a_roles.seed_roles",
        "fake_seeders.a_roles.seed_users",
        "fake_seeders.b_places.seed_places",
    ]
