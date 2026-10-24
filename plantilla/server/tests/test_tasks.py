"""The periodic tasks."""

import os
import time
from pathlib import Path
from uuid import UUID

import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import files


async def test_sweep_deletes_only_old_files_without_row(
    session: AsyncSession, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A file with a row, or newer than the margin, stays."""
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
