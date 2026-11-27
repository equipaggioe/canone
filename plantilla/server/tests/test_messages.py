"""The messages of a request go after the commit, and best effort."""

from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta

import httpx
import pytest
from fastapi import FastAPI, HTTPException
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncConnection

from app import errors
from app.dependencies import SessionDep
from app.errors import KeptError
from app.services import messages, transport

probe = FastAPI()
errors.install(probe)


async def send() -> None:
    """Send an SMS that expires in a minute."""
    await transport.sms("+56221234567", "Hola", datetime.now(UTC) + timedelta(minutes=1))


@probe.post("/{outcome}")
async def queue(outcome: str, session: SessionDep) -> None:
    """Queue a message, then end as the outcome says."""
    messages.later(session, send)
    if outcome == "fails":
        raise HTTPException(409)
    if outcome == "keeps":
        raise KeptError(HTTPException(401))


@pytest.fixture
async def probed(database: AsyncConnection) -> AsyncIterator[AsyncClient]:
    """Call the probe inside the transaction of the test."""
    async with AsyncClient(transport=ASGITransport(app=probe), base_url="http://test") as client:
        yield client


@pytest.mark.parametrize(
    ("outcome", "status", "count"), [("ends", 200, 1), ("keeps", 401, 1), ("fails", 409, 0)]
)
async def test_messages_go_after_the_commit(
    probed: AsyncClient, sent: list[httpx.Request], outcome: str, status: int, count: int
) -> None:
    """A request that rolls back sends nothing; a commit sends."""
    assert (await probed.post(f"/{outcome}")).status_code == status
    assert len(sent) == count


async def test_failed_delivery_does_not_fail_the_request(
    probed: AsyncClient, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """A transport failing goes to the log and leaves the answer."""

    async def refuse(to: str, text: str, expires: datetime) -> None:
        """Fail as a transport that cannot reach its queue."""
        raise ConnectionError(to)

    monkeypatch.setattr(transport, "sms", refuse)
    assert (await probed.post("/ends")).status_code == 200
    assert "A message did not go out" in caplog.text
