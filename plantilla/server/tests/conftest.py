"""Fixtures: every session of a test joins one transaction."""

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import SessionFactory, engine
from app.main import app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Run the tests on asyncio, the only loop asyncpg supports."""
    return "asyncio"


@pytest.fixture
async def database(monkeypatch: pytest.MonkeyPatch) -> AsyncIterator[None]:
    """Bind the session factory to a transaction that is rolled back."""
    async with engine.connect() as connection:
        transaction = await connection.begin()
        monkeypatch.setitem(SessionFactory.kw, "bind", connection)
        monkeypatch.setitem(SessionFactory.kw, "join_transaction_mode", "create_savepoint")
        yield
        await transaction.rollback()
    # Each test runs in its own event loop, and a pooled
    # connection belongs to the old one.
    await engine.dispose()


@pytest.fixture
async def session(database: None) -> AsyncIterator[AsyncSession]:
    """Open a session of the test, inside its transaction."""
    async with SessionFactory() as session:
        yield session


@pytest.fixture
async def client(database: None) -> AsyncIterator[AsyncClient]:
    """Call the app in process, inside the transaction of the test."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
