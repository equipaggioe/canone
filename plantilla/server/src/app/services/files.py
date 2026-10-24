"""The files of the users, on disk."""

import os
import time
from pathlib import Path

import sqlalchemy as sa

from app import models
from app.database import SessionFactory

# Lets an upload that has not committed its row yet finish.
MARGIN_SECONDS = 3600


def folder() -> Path:
    """Return the folder of the files: the StateDirectory=."""
    return Path(os.environ["STATE_DIRECTORY"])


def file_tables() -> list[sa.Table]:
    """Return every table that holds the rows of files.

    Importing app.models fills the metadata with every table.
    """
    tables = models.base.Base.metadata.tables
    return [table for name, table in tables.items() if name.endswith("_file")]


async def known_names(names: list[str]) -> set[str]:
    """Return the names that are the id of a row in some _file table."""
    known: set[str] = set()
    async with SessionFactory() as session:
        for table in file_tables():
            column = table.c.id
            query = sa.select(sa.cast(column, sa.Text)).where(sa.cast(column, sa.Text).in_(names))
            known.update((await session.scalars(query)).all())
    return known


async def sweep() -> None:
    """Delete every file older than the margin that has no row."""
    cutoff = time.time() - MARGIN_SECONDS
    old = {path.name: path for path in folder().iterdir() if path.stat().st_mtime < cutoff}
    if not old:
        return
    known = await known_names(list(old))
    for name, path in old.items():
        if name not in known:
            path.unlink()
