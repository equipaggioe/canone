"""The engine, the session factory, and the migrations."""

import importlib
import inspect
import pkgutil
from collections.abc import Awaitable, Callable

from alembic.config import Config
from sqlalchemy import Connection
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from alembic import command
from app.config import settings

# canone ADR-0199: a pooled connection that PostgreSQL closed on a
# restart fails the request that takes it; the ping replaces it
# first.
engine = create_async_engine(settings.database_url, pool_pre_ping=True)
SessionFactory = async_sessionmaker(engine, expire_on_commit=False)

Seeder = Callable[[AsyncSession], Awaitable[None]]


def seeders(package: str) -> list[Seeder]:
    """Return the seed_ functions of each module of package, by name."""
    found: list[Seeder] = []
    modules = pkgutil.iter_modules(importlib.import_module(package).__path__)
    for name in sorted(module.name for module in modules):
        module = importlib.import_module(f"{package}.{name}")
        for attribute, value in sorted(vars(module).items()):
            defined = getattr(value, "__module__", None) == module.__name__
            if attribute.startswith("seed_") and inspect.iscoroutinefunction(value) and defined:
                found.append(value)
    return found


async def seed(connection: AsyncConnection, package: str) -> None:
    """Run the seeders of package in the transaction of connection."""
    async with AsyncSession(bind=connection) as session:
        for seeder in seeders(package):
            await seeder(session)
        await session.flush()


def upgrade(connection: Connection, config: Config) -> None:
    """Run the migrations on connection, in its transaction."""
    config.attributes["connection"] = connection
    command.upgrade(config, "head")


async def migrate() -> None:
    """Run the migrations and the seeders in one transaction.

    A seeder that fails undoes the migrations, and deploy.py goes back
    to the previous version.
    """
    async with engine.begin() as connection:
        await connection.run_sync(upgrade, Config("alembic.ini"))
        await seed(connection, "app.seeders")


async def mock() -> None:
    """Load the example data, only in development."""
    async with engine.begin() as connection:
        await seed(connection, "app.mock_data")
