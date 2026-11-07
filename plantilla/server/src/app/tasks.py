"""Run a task of the machine: python -m app.tasks <task>."""

import argparse
import asyncio
import importlib
import inspect
import pkgutil
from collections.abc import Awaitable, Callable

from alembic.config import Config
from sqlalchemy import Connection
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession

from alembic import command
from app.database import engine
from app.services import events, files

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


TASKS: dict[str, Callable[[], Awaitable[None]]] = {
    "migrate": migrate,
    "mock": mock,
    "purge": events.purge,
    "sweep": files.sweep,
}


async def run(task: str) -> None:
    """Run the task, and close the pooled connections."""
    try:
        await TASKS[task]()
    finally:
        await engine.dispose()


def main() -> None:
    """Read the task from the command line and run it."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", choices=TASKS)
    asyncio.run(run(parser.parse_args().task))


if __name__ == "__main__":
    main()
