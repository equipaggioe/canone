"""Whether the server reaches its database, and what to alert on."""

import shutil
from datetime import UTC, datetime

import sqlalchemy as sa
from sqlalchemy.exc import SQLAlchemyError

from app.database import SessionFactory, engine
from app.enums import EventLevel
from app.models.event.event_log import EventLog
from app.services import files


async def database_answers() -> bool:
    """Run SELECT 1 on a connection of its own."""
    try:
        async with engine.connect() as connection:
            await connection.execute(sa.text("SELECT 1"))
    except (SQLAlchemyError, OSError):
        return False
    return True


async def last_event() -> datetime | None:
    """Return when the last event of any level happened."""
    async with SessionFactory() as session:
        return await session.scalar(sa.select(sa.func.max(EventLog.occurred_at)))


async def last_critical() -> datetime | None:
    """Return when the last critical event happened."""
    query = sa.select(sa.func.max(EventLog.occurred_at)).where(
        EventLog.level == EventLevel.CRITICAL
    )
    async with SessionFactory() as session:
        return await session.scalar(query)


async def settled_events(after: tuple[int, int] | None, size: int) -> list[EventLog]:
    """Return events by transaction, below the oldest one still open.

    ADR-0100: a transaction that commits late writes rows below those
    already read; below the oldest open one, no row is still to come.
    """
    oldest = sa.func.pg_snapshot_xmin(sa.func.pg_current_snapshot())
    query = sa.select(EventLog).where(EventLog.xid < oldest)
    if after is not None:
        query = query.where(sa.tuple_(EventLog.xid, EventLog.id) > after)
    query = query.order_by(EventLog.xid, EventLog.id).limit(size)
    async with SessionFactory() as session:
        return list(await session.scalars(query))


def last_backup() -> datetime | None:
    """Return the time of last-backup, which each good backup touches.

    It is in the folder of the app, above the folder of the files.
    """
    try:
        seconds = (files.folder().parent / "last-backup").stat().st_mtime
    except FileNotFoundError:
        return None
    return datetime.fromtimestamp(seconds, UTC)


def disk_usage() -> tuple[int, int]:
    """Return the free and the total bytes of the disk of the files.

    Free is what a user without privileges may still write, as
    PostgreSQL does.
    """
    usage = shutil.disk_usage(files.folder())
    return usage.free, usage.total
