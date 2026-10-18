"""Dependencies shared by the routers."""

import re
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import VERSION, settings
from app.database import SessionFactory
from app.errors import CLIENT_OUTDATED, AppError


async def get_session() -> AsyncIterator[AsyncSession]:
    """Open one session and one transaction per request."""
    async with SessionFactory.begin() as session:
        yield session


# Commit before the response, so a failed commit reaches the client.
SessionDep = Annotated[AsyncSession, Depends(get_session, scope="function")]


def version_numbers(version: str) -> tuple[int, ...]:
    """Split MAJOR.MINOR.PATCH into integers, or none if malformed."""
    if not re.fullmatch(VERSION, version):
        return ()
    return tuple(int(number) for number in version.split("."))


async def check_client_version(user_agent: Annotated[str, Header()] = "") -> None:
    """Reject an installable client older than its minimum version."""
    piece, _, version = user_agent.split(" ", 1)[0].partition("/")
    minimum = settings.min_client_versions.get(piece)
    # An empty tuple sorts first: a malformed version is outdated.
    if minimum is not None and version_numbers(version) < version_numbers(minimum):
        raise AppError(CLIENT_OUTDATED)
