"""The files of the users, on disk."""

import os
import shutil
import time
import warnings
from collections.abc import Collection
from http import HTTPStatus
from io import BytesIO
from pathlib import Path

import sqlalchemy as sa
from fastapi import HTTPException, UploadFile
from PIL import Image, ImageOps
from starlette.responses import FileResponse

from app.database import SessionFactory
from app.models.base import Base

# Lets an upload that has not committed its row yet finish.
MARGIN_SECONDS = 3600


def folder() -> Path:
    """Return the folder of the files: the StateDirectory=."""
    return Path(os.environ["STATE_DIRECTORY"])


async def read(upload: UploadFile, limit: int) -> bytes:
    """Read an upload, or answer 413 past the limit of its resource."""
    data = await upload.read(limit + 1)
    if len(data) > limit:
        raise HTTPException(HTTPStatus.CONTENT_TOO_LARGE)
    return data


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


def sizes(data: bytes, formats: Collection[str], sides: dict[str, int]) -> dict[str, bytes]:
    """Decode an image once and encode it as WebP in each size.

    Each size is upright and without metadata. `sides` names each size
    by the length of its longer side, which keeps the ratio, and the
    original is not kept. It opens only the formats of the resource,
    and an image past the pixel limit of Pillow fails. It blocks: run
    it in a thread.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        with Image.open(BytesIO(data), formats=list(formats)) as image:
            upright = ImageOps.exif_transpose(image)
            found: dict[str, bytes] = {}
            for name, side in sides.items():
                output = BytesIO()
                ImageOps.contain(upright, (side, side)).save(output, format="WEBP")
                found[name] = output.getvalue()
    return found


def store_sizes(row_id: str, found: dict[str, bytes]) -> Path:
    """Write each size as <size>.webp in the folder of its row's id.

    Return the folder.
    """
    target = folder() / row_id
    target.mkdir()
    for name, data in found.items():
        (target / f"{name}.webp").write_bytes(data)
    return target


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
    tables = Base.metadata.tables
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
    """Delete every file or folder of sizes older than the margin.

    Only those that no row names.
    """
    cutoff = time.time() - MARGIN_SECONDS
    old = {path.name: path for path in folder().iterdir() if path.stat().st_mtime < cutoff}
    if not old:
        return
    known = await known_names(list(old))
    for name, path in old.items():
        if name not in known:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
