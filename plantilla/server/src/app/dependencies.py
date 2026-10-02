"""Dependencies shared by the routers."""

from collections.abc import AsyncIterator
from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, Header
from packaging.version import Version
from sqlalchemy.ext.asyncio import AsyncSession

from app import problems
from app.config import settings
from app.database import SessionFactory
from app.errors import AppError


async def get_session() -> AsyncIterator[AsyncSession]:
    """Open one session and one transaction per request."""
    async with SessionFactory.begin() as session:
        yield session


# Commit before the response, so a failed commit reaches the client.
SessionDep = Annotated[AsyncSession, Depends(get_session, scope="function")]


async def check_client_version(user_agent: Annotated[str, Header()] = "") -> None:
    """Reject an installable client older than its minimum version."""
    piece, _, version = user_agent.split(" ", 1)[0].partition("/")
    minimum = settings.min_client_versions.get(piece)
    if minimum is not None and Version(version) < Version(minimum):
        raise AppError(problems.CLIENT_OUTDATED, "Client outdated", HTTPStatus.BAD_REQUEST)
