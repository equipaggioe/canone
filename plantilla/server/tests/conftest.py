"""Fixtures: a client and a session rolled back after each test."""

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import engine
from app.dependencies import get_session
from app.main import app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Run the tests on asyncio, the only loop asyncpg supports."""
    return "asyncio"


@pytest.fixture
async def session() -> AsyncIterator[AsyncSession]:
    """Open a session inside a transaction that is rolled back."""
    async with engine.connect() as connection:
        transaction = await connection.begin()
        async with AsyncSession(
            bind=connection, join_transaction_mode="create_savepoint", expire_on_commit=False
        ) as session:
            yield session
        await transaction.rollback()
    # Each test runs in its own event loop, and a pooled
    # connection belongs to the old one.
    await engine.dispose()


@pytest.fixture
async def client(session: AsyncSession) -> AsyncIterator[AsyncClient]:
    """Call the app in process, sharing the test session."""
    app.dependency_overrides[get_session] = lambda: session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()
