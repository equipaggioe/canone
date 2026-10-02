"""Whether the server reaches its database."""

import sqlalchemy as sa
from sqlalchemy.exc import SQLAlchemyError

from app.database import engine


async def database_answers() -> bool:
    """Run SELECT 1 on a connection of its own."""
    try:
        async with engine.connect() as connection:
            await connection.execute(sa.text("SELECT 1"))
    except (SQLAlchemyError, OSError):
        return False
    return True
