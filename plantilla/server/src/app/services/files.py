"""The files of the users, on disk."""

import os
import time
import warnings
from collections.abc import Collection
from io import BytesIO
from pathlib import Path

import sqlalchemy as sa
from PIL import Image, ImageOps
from starlette.responses import FileResponse

from app import models
from app.database import SessionFactory

# Lets an upload that has not committed its row yet finish.
MARGIN_SECONDS = 3600


def folder() -> Path:
    """Return the folder of the files: the StateDirectory=."""
    return Path(os.environ["STATE_DIRECTORY"])


def reencode(data: bytes, formats: Collection[str]) -> bytes:
    """Decode an image and encode it again, upright, without metadata.

    It opens only the formats of the resource, and an image past the
    pixel limit of Pillow fails. It blocks: run it in a thread.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        with Image.open(BytesIO(data), formats=list(formats)) as image:
            upright = ImageOps.exif_transpose(image)
            output = BytesIO()
            upright.save(output, format=image.format)
    return output.getvalue()


def download(path: Path, media_type: str | None, name: str) -> FileResponse:
    """Answer a file as an attachment, never shown in place."""
    return FileResponse(
        path,
        media_type=media_type or "application/octet-stream",
        filename=name,
        content_disposition_type="attachment",
    )


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
            query = sa.select(sa.cast(column, sa.Text())).where(
                sa.cast(column, sa.Text()).in_(names)
            )
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
