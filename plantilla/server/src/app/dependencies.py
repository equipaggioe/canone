"""Dependencies shared by the routers."""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import SessionFactory


async def get_session() -> AsyncIterator[AsyncSession]:
    """Open one session per request."""
    async with SessionFactory() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
