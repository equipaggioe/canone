"""Fixtures: every session of a test joins one transaction."""

from collections.abc import AsyncIterator

import pytest
import sqlalchemy as sa
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.engine import AdaptedConnection
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession
from sqlalchemy.pool import ConnectionPoolEntry

from app.database import SessionFactory, engine
from app.main import app
from app.models.event.event_log import EventLog

# The roles of the server and of the owner of the schema, as
# install.py creates them.
SERVER = "PRODUCTO"
OWNER = "PRODUCTO_owner"


@event.listens_for(engine.sync_engine, "connect")
def run_as_server(connection: AdaptedConnection, entry: ConnectionPoolEntry) -> None:
    """Give each connection the privileges of the server.

    The role lasts the whole connection, outside any transaction.
    """
    connection.run_async(lambda driver: driver.execute(f"SET ROLE {SERVER}"))


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Run the tests on asyncio, the only loop asyncpg supports."""
    return "asyncio"


@pytest.fixture
async def database(monkeypatch: pytest.MonkeyPatch) -> AsyncIterator[AsyncConnection]:
    """Bind the session factory to a transaction that is rolled back."""
    async with engine.connect() as connection:
        transaction = await connection.begin()
        monkeypatch.setitem(SessionFactory.kw, "bind", connection)
        monkeypatch.setitem(SessionFactory.kw, "join_transaction_mode", "create_savepoint")
        yield connection
        await transaction.rollback()
    # Each test runs in its own event loop, and a pooled
    # connection belongs to the old one.
    await engine.dispose()


@pytest.fixture
async def owner(database: AsyncConnection) -> None:
    """Run the test as the owner of the schema, like the purge."""
    await database.exec_driver_sql(f"SET LOCAL ROLE {OWNER}")


@pytest.fixture
async def session(database: AsyncConnection) -> AsyncIterator[AsyncSession]:
    """Open a session of the test, inside its transaction."""
    async with SessionFactory() as session:
        yield session


@pytest.fixture
async def client(database: AsyncConnection) -> AsyncIterator[AsyncClient]:
    """Call the app in process, inside the transaction of the test."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.fixture
async def committed() -> AsyncIterator[list[int]]:
    """Collect the events a test commits; the owner deletes them."""
    ids: list[int] = []
    yield ids
    async with engine.begin() as connection:
        await connection.exec_driver_sql(f"SET LOCAL ROLE {OWNER}")
        await connection.execute(sa.delete(EventLog).where(EventLog.id.in_(ids)))
