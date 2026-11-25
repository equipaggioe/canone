"""The WebSocket: its handshake, its messages and its end."""

import asyncio
import json
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

import pytest
import sqlalchemy as sa
from httpx import AsyncClient
from httpx_ws import AsyncWebSocketSession, WebSocketDisconnect, WebSocketUpgradeError, aconnect_ws
from httpx_ws.transport import ASGIWebSocketTransport
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, SessionTransaction
from starlette.websockets import WebSocket
from valkey.asyncio import Valkey

from app import errors, store
from app.config import settings
from app.enums import Role, SessionKind
from app.main import app
from app.models.account.account import Account
from app.models.account.account_session import AccountSession
from app.models.event.event_log import EventLog
from app.schemas.websocket import ErrorMessage, MessageProblem
from app.services import channel, events, limits, sessions, websocket
from app.services.sessions import Client, Issued

URL = "http://test/api/websocket"
CLIENT = Client("127.0.0.1", "test")
OTHER = "otra@example.com"


@pytest.fixture
async def wired(client: AsyncClient) -> AsyncIterator[AsyncClient]:
    """Call the app in process, its WebSocket included."""
    async with AsyncClient(
        transport=ASGIWebSocketTransport(app=app), base_url="http://test"
    ) as wired:
        yield wired


@pytest.fixture
async def account(session: AsyncSession) -> Account:
    """Create an account."""
    row = Account(email="ana@example.com", role=Role.USER, language="es")
    session.add(row)
    await session.flush()
    return row


@pytest.fixture
async def issued(session: AsyncSession, account: Account) -> Issued:
    """Open an app session as a login would."""
    tokens = await sessions.open_app(session, account, CLIENT, "es")
    await session.flush()
    return tokens


@pytest.fixture
async def cookie(session: AsyncSession, account: Account) -> str:
    """Open a web session as a login would."""
    token, _ = await sessions.open_web(session, account, CLIENT, "es")
    await session.flush()
    return token


@pytest.fixture
def recorded(monkeypatch: pytest.MonkeyPatch) -> list[EventLog]:
    """Keep the events that go in their own transaction."""
    found: list[EventLog] = []

    async def record(row: EventLog) -> None:
        """Keep an event."""
        found.append(row)

    monkeypatch.setattr(events, "record", record)
    return found


def bearer(issued: Issued) -> dict[str, str]:
    """Present the access token of an app."""
    return {"Authorization": f"Bearer {issued.access_token}"}


def web(cookie: str, origin: str | None = "https://test") -> dict[str, str]:
    """Present the cookie of the web, from an origin."""
    headers = {"Cookie": f"{sessions.COOKIE}={cookie}"}
    return headers if origin is None else {**headers, "Origin": origin}


def conflict() -> ErrorMessage:
    """Build a message of the server."""
    return ErrorMessage(data=MessageProblem.model_validate(errors.blank(409)))


async def closed(socket: AsyncWebSocketSession) -> int:
    """Wait for the server to close, and return its code."""
    with pytest.raises(WebSocketDisconnect) as error:
        await socket.receive_text(timeout=5)
    return error.value.code


async def alive(socket: AsyncWebSocketSession) -> bool:
    """Tell whether the connection answers."""
    await socket.send_text("{")
    answer = json.loads(await socket.receive_text(timeout=5))
    return bool(answer["data"]["status"] == 400)


async def refused(wired: AsyncClient, headers: dict[str, str]) -> tuple[int, dict[str, Any], str]:
    """Return the status and the problem of a refused handshake."""
    with pytest.raises(WebSocketUpgradeError) as error:
        async with aconnect_ws(URL, wired, headers=headers):
            pass
    response = error.value.response
    assert response.headers["content-type"] == errors.PROBLEM_JSON
    return (
        response.status_code,
        json.loads(await response.aread()),
        response.headers.get("retry-after", ""),
    )


async def places(account_id: UUID) -> int:
    """Count the places taken of an account."""
    return int(await store.client.zcard(websocket.place_key(account_id)))


async def test_the_web_and_an_app_connect(wired: AsyncClient, issued: Issued, cookie: str) -> None:
    """The web by its cookie, and an app by its token."""
    for headers in (bearer(issued), web(cookie)):
        async with aconnect_ws(URL, wired, headers=headers) as socket:
            assert await alive(socket)


async def test_no_session_is_4401(
    wired: AsyncClient, session: AsyncSession, issued: Issued, cookie: str
) -> None:
    """No credential, a wrong one or an expired one, all accepted.

    Each token holds only as what it is.
    """
    wrong: list[dict[str, str]] = [
        {},
        {"Authorization": "Bearer wrong"},
        {"Authorization": f"Basic {issued.access_token}"},
        {"Authorization": f"Bearer {cookie}"},
        web(issued.access_token),
        {**web(cookie), "Authorization": "Basic x"},
    ]
    for headers in wrong:
        async with aconnect_ws(URL, wired, headers=headers) as socket:
            assert await closed(socket) == 4401, headers
    past = datetime.now(UTC) - timedelta(seconds=1)
    await session.execute(
        sa.update(AccountSession)
        .where(AccountSession.id == issued.session_id)
        .values(token_expires_at=past)
    )
    async with aconnect_ws(URL, wired, headers=bearer(issued)) as socket:
        assert await closed(socket) == 4401


@pytest.mark.parametrize("origin", ["https://evil.example", None])
async def test_cookie_needs_the_origin(
    wired: AsyncClient,
    issued: Issued,
    cookie: str,
    recorded: list[EventLog],
    origin: str | None,
) -> None:
    """A handshake with the cookie from elsewhere is a 403.

    One with Authorization does not look at it.
    """
    status, problem, _ = await refused(wired, web(cookie, origin))
    assert (status, problem["type"]) == (403, "about:blank")
    assert [row.action for row in recorded] == ["malicious_csrf"]
    async with aconnect_ws(
        URL, wired, headers={**web(cookie, origin), **bearer(issued)}
    ) as socket:
        assert await alive(socket)


async def test_outdated_app_does_not_connect(
    wired: AsyncClient, issued: Issued, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The handshake of an old app is a 400 of its type."""
    monkeypatch.setattr(settings, "min_client_versions", {"mobile": "2.0.0"})
    status, problem, _ = await refused(wired, {**bearer(issued), "User-Agent": "mobile/1.0.0"})
    assert (status, problem["type"]) == (400, errors.CLIENT_OUTDATED.uri)


async def test_eleventh_connection_is_a_429(
    wired: AsyncClient,
    session: AsyncSession,
    account: Account,
    issued: Issued,
    recorded: list[EventLog],
) -> None:
    """Ten of an account connect; a place that nobody renews frees."""
    key = websocket.place_key(account.id)
    until = limits.now() + 60_000
    await store.client.zadd(key, {f"p{number}": until for number in range(9)})
    other = Account(email=OTHER, role=Role.USER, language="es")
    session.add(other)
    await session.flush()
    theirs = await sessions.open_app(session, other, CLIENT, "es")
    await session.flush()
    async with aconnect_ws(URL, wired, headers=bearer(issued)) as socket:
        assert await alive(socket)
        recorded.clear()
        status, problem, retry = await refused(wired, bearer(issued))
        assert (status, problem["type"], retry) == (429, "about:blank", "30")
        assert [row.action for row in recorded] == ["excess_rate_limit_exceeded"]
        async with aconnect_ws(URL, wired, headers=bearer(theirs)) as free:
            assert await alive(free)
    await asyncio.sleep(0.2)
    assert await places(account.id) == 9
    await store.client.zadd(key, {f"p{number}": limits.now() - 1 for number in range(9)})
    async with aconnect_ws(URL, wired, headers=bearer(issued)) as socket:
        assert await alive(socket)
        assert await places(account.id) == 1


async def test_connection_renews_its_place(
    wired: AsyncClient, account: Account, issued: Issued, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The place lasts a minute, and is renewed every 30 seconds."""
    assert websocket.RENEWAL == timedelta(seconds=30)
    monkeypatch.setattr(websocket, "RENEWAL", timedelta(milliseconds=50))
    key = websocket.place_key(account.id)
    async with aconnect_ws(URL, wired, headers=bearer(issued)) as socket:
        assert await alive(socket)
        ((place, until),) = await store.client.zrange(key, 0, -1, withscores=True)
        assert 55_000 < until - limits.now() <= 60_000
        await store.client.zadd(key, {place: 0})
        await asyncio.sleep(0.2)
        score = await store.client.zscore(key, place)
        assert score is not None
        assert score > limits.now()
    await asyncio.sleep(0.2)
    assert await places(account.id) == 0


@pytest.mark.parametrize(
    "ending", ["logout", "one", "others", "reuse", "login", "disabled", "deleted", "all"]
)
async def test_ended_session_closes_its_connections(
    wired: AsyncClient,
    session: AsyncSession,
    account: Account,
    issued: Issued,
    ending: str,
) -> None:
    """Whatever ends the session closes them, and no other's."""
    other = await sessions.open_app(session, account, CLIENT, "es")
    boss = Account(email=OTHER, role=Role.SUPERADMIN, language="es")
    session.add(boss)
    await session.flush()
    chief = bearer(await sessions.open_app(session, boss, CLIENT, "es"))
    await session.flush()
    async with (
        aconnect_ws(URL, wired, headers=bearer(issued)) as socket,
        aconnect_ws(URL, wired, headers=bearer(other)) as stays,
    ):
        assert await alive(socket)
        assert await alive(stays)
        if ending == "logout":
            await wired.post("/api/auth/logout", headers=bearer(issued))
        elif ending == "one":
            path = f"/api/account/sessions/{issued.session_id}"
            await wired.delete(path, headers=bearer(other))
        elif ending == "others":
            await wired.delete("/api/account/sessions", headers=bearer(other))
        elif ending == "reuse":
            forged = sessions.sign(issued.session_id, "wrong")
            form = {"grant_type": "refresh_token", "refresh_token": forged}
            await wired.post("/api/auth/token", data=form)
        elif ending == "login":
            await sessions.discard(session, issued.access_token, SessionKind.APP)
            await channel.flush(session)
        elif ending == "disabled":
            await wired.post(f"/api/accounts/{account.id}/disable", headers=chief)
        elif ending == "deleted":
            await wired.delete(f"/api/accounts/{account.id}", headers=chief)
        else:
            await wired.delete("/api/accounts/sessions", headers=chief)
        assert await closed(socket) == 4401
        if ending in ("disabled", "deleted", "all"):
            assert await closed(stays) == 4401
        else:
            assert await alive(stays)


async def test_close_goes_after_the_commit(
    wired: AsyncClient, issued: Issued, session: AsyncSession, account: Account
) -> None:
    """What a request queued waits for its commit."""
    async with aconnect_ws(URL, wired, headers=bearer(issued)) as socket:
        channel.close(session, account.id, [issued.session_id])
        assert await alive(socket)
        await channel.flush(session)
        assert await closed(socket) == 4401


async def test_session_that_ends_during_the_handshake_is_4401(
    wired: AsyncClient,
    session: AsyncSession,
    issued: Issued,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Between its check and its channel, nobody would tell it."""
    join = websocket.Hub.join

    async def late(hub: websocket.Hub, connection: websocket.Connection) -> None:
        """End the session before the channel is subscribed."""
        await session.execute(
            sa.delete(AccountSession).where(AccountSession.id == issued.session_id)
        )
        await join(hub, connection)

    monkeypatch.setattr(websocket.Hub, "join", late)
    async with aconnect_ws(URL, wired, headers=bearer(issued)) as socket:
        assert await closed(socket) == 4401


async def test_app_connection_ends_with_its_token(
    wired: AsyncClient, session: AsyncSession, issued: Issued
) -> None:
    """At the expiry of the last token it presented, not before."""
    soon = datetime.now(UTC) + timedelta(seconds=1)
    await session.execute(
        sa.update(AccountSession)
        .where(AccountSession.id == issued.session_id)
        .values(token_expires_at=soon)
    )
    async with (
        aconnect_ws(URL, wired, headers=bearer(issued)) as ends,
        aconnect_ws(URL, wired, headers=bearer(issued)) as goes_on,
    ):
        form = {"grant_type": "refresh_token", "refresh_token": issued.refresh_token}
        renewed = (await wired.post("/api/auth/token", data=form)).json()["access_token"]
        # The refresh by itself closes nothing.
        assert await alive(ends)
        message = {"type": "access_token", "data": {"accessToken": renewed}}
        await goes_on.send_text(json.dumps(message))
        assert await closed(ends) == 4401
        assert datetime.now(UTC) >= soon
        assert await alive(goes_on)


@pytest.mark.parametrize("whose", ["nobody", "another"])
async def test_token_of_another_session_is_4401(
    wired: AsyncClient, session: AsyncSession, account: Account, issued: Issued, whose: str
) -> None:
    """A token that does not hold, or of another session, closes it."""
    other = await sessions.open_app(session, account, CLIENT, "es")
    await session.flush()
    token = other.access_token if whose == "another" else "wrong"
    async with aconnect_ws(URL, wired, headers=bearer(issued)) as socket:
        message = {"type": "access_token", "data": {"accessToken": token}}
        await socket.send_text(json.dumps(message))
        assert await closed(socket) == 4401


async def test_web_connection_ends_30_days_after_the_last_use(
    wired: AsyncClient, session: AsyncSession, cookie: str
) -> None:
    """Of the session, read again when it would expire.

    The connection is no use of the session.
    """
    used = datetime.now(UTC) - sessions.IDLE + timedelta(seconds=1)
    await session.execute(sa.update(AccountSession).values(last_used_at=used))
    async with aconnect_ws(URL, wired, headers=web(cookie)) as socket:
        assert await alive(socket)
        later = used + timedelta(seconds=1)
        await session.execute(sa.update(AccountSession).values(last_used_at=later))
        await asyncio.sleep(1.2)
        assert await alive(socket)
        assert await closed(socket) == 4401
    assert await session.scalar(sa.select(AccountSession.last_used_at)) == later


async def test_silent_connection_stays(
    wired: AsyncClient, issued: Issued, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Waiting for a message is no failure of Valkey."""
    impatient = Valkey.from_url(settings.valkey_url, socket_timeout=0.1)
    monkeypatch.setattr(store, "client", impatient)
    async with aconnect_ws(URL, wired, headers=bearer(issued)) as socket:
        await asyncio.sleep(0.5)
        assert await alive(socket)
    await asyncio.sleep(0.2)
    await impatient.aclose()


async def test_lost_subscription_is_1012(
    wired: AsyncClient, issued: Issued, caplog: pytest.LogCaptureFixture
) -> None:
    """What was published meanwhile is lost; the next one connects."""
    async with aconnect_ws(URL, wired, headers=bearer(issued)) as socket:
        assert await alive(socket)
        await store.client.execute_command("CLIENT", "KILL", "TYPE", "pubsub")
        assert await closed(socket) == 1012
    assert "The subscription to Valkey was lost" in caplog.text
    async with aconnect_ws(URL, wired, headers=bearer(issued)) as socket:
        assert await alive(socket)


@pytest.mark.parametrize(
    ("text", "status", "pointer", "action"),
    [
        ("{", 400, None, "input_validation_fail"),
        ('{"type": "a", "type": "a"}', 422, "", "input_validation_fail"),
        ("[]", 422, "", "input_validation_fail"),
        ('{"data": {}}', 422, "/type", "input_validation_discrete_fail"),
        ('{"type": "unknown", "data": {}}', 422, "/type", "input_validation_discrete_fail"),
        (
            '{"type": "access_token", "data": {}}',
            422,
            "/data/accessToken",
            "input_validation_fail",
        ),
        (
            '{"type": "access_token", "data": {"accessToken": "a", "more": 1}}',
            422,
            "/data/more",
            "malicious_extraneous",
        ),
    ],
)
async def test_message_that_is_not_taken_is_an_error(
    wired: AsyncClient,
    issued: Issued,
    recorded: list[EventLog],
    text: str,
    status: int,
    pointer: str | None,
    action: str,
) -> None:
    """The server answers its problem and its event, and goes on."""
    async with aconnect_ws(URL, wired, headers=bearer(issued)) as socket:
        await socket.send_text(text)
        answer = json.loads(await socket.receive_text(timeout=5))
        assert set(answer) == {"type", "data"}
        assert (answer["type"], answer["data"]["status"]) == ("error", status)
        assert len(answer["data"]["traceId"]) == 32
        assert ("errors" in answer["data"]) == (pointer is not None)
        if pointer is not None:
            assert answer["data"]["type"] == errors.VALIDATION.uri
            assert [item["pointer"] for item in answer["data"]["errors"]] == [pointer]
        assert [row.action for row in recorded] == [action]
        assert await alive(socket)


async def test_message_that_fails_is_a_500_and_the_app_goes_on(
    wired: AsyncClient,
    issued: Issued,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Its exception goes to the log."""

    async def fail(*_: object) -> None:
        """Fail as a handler would."""
        raise RuntimeError("broken")

    monkeypatch.setattr(websocket, "handle", fail)
    async with aconnect_ws(URL, wired, headers=bearer(issued)) as socket:
        await socket.send_text('{"type": "access_token", "data": {"accessToken": "a"}}')
        answer = json.loads(await socket.receive_text(timeout=5))
        assert answer["data"]["status"] == 500
        assert "broken" not in json.dumps(answer)
        assert await alive(socket)
    assert "broken" in caplog.text


async def test_binary_message_is_1003(wired: AsyncClient, issued: Issued) -> None:
    """Every message is text."""
    async with aconnect_ws(URL, wired, headers=bearer(issued)) as socket:
        await socket.send_bytes(b"{}")
        assert await closed(socket) == 1003


async def test_message_past_the_hundred_is_1008(
    wired: AsyncClient,
    account: Account,
    issued: Issued,
    recorded: list[EventLog],
) -> None:
    """A hundred a minute, by account."""
    key = f"limit:websocket:messages:{account.id}"
    await store.client.zadd(key, {str(uuid4()): limits.now() for _ in range(99)})
    async with aconnect_ws(URL, wired, headers=bearer(issued)) as socket:
        assert await alive(socket)
        recorded.clear()
        await socket.send_text("{")
        assert await closed(socket) == 1008
    assert [row.action for row in recorded] == ["excess_rate_limit_exceeded"]


async def test_message_reaches_each_connection_of_the_account(
    wired: AsyncClient, session: AsyncSession, account: Account, issued: Issued, cookie: str
) -> None:
    """Each connection of the account, and none of another's."""
    other = Account(email=OTHER, role=Role.USER, language="es")
    session.add(other)
    await session.flush()
    theirs = await sessions.open_app(session, other, CLIENT, "es")
    await session.flush()
    message = conflict()
    async with (
        aconnect_ws(URL, wired, headers=bearer(issued)) as app_socket,
        aconnect_ws(URL, wired, headers=web(cookie)) as web_socket,
        aconnect_ws(URL, wired, headers=bearer(theirs)) as stranger,
    ):
        channel.send(session, account.id, message)
        await channel.flush(session)
        for socket in (app_socket, web_socket):
            answer = json.loads(await socket.receive_text(timeout=5))
            assert (answer["type"], answer["data"]["status"]) == ("error", 409)
        assert await alive(stranger)


async def test_connection_with_a_hundred_to_send_is_1013(
    session: AsyncSession, issued: Issued
) -> None:
    """The queue takes a hundred, and one more ends the connection."""
    row = await session.get_one(AccountSession, issued.session_id)
    connection = websocket.Connection(row)
    for number in range(100):
        connection.put(str(number))
    assert not connection.ended.is_set()
    connection.put("one more")
    assert (connection.ended.is_set(), connection.code) == (True, 1013)
    connection.end(1012)
    assert connection.code == 1013


async def test_lost_subscription_starts_over_with_a_stuck_connection(
    wired: AsyncClient,
    session: AsyncSession,
    account: Account,
    issued: Issued,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The next connection subscribes again, though one has not left."""

    async def never(*_: object) -> None:
        """Wait as Uvicorn does on a client that stopped reading."""
        await asyncio.Event().wait()

    async with aconnect_ws(URL, wired, headers=bearer(issued)) as stuck:
        assert await alive(stuck)
        with monkeypatch.context() as patch:
            patch.setattr(WebSocket, "close", never)
            await store.client.execute_command("CLIENT", "KILL", "TYPE", "pubsub")
            await asyncio.sleep(0.2)
            async with aconnect_ws(URL, wired, headers=bearer(issued)) as socket:
                assert await alive(socket)
                channel.send(session, account.id, conflict())
                await channel.flush(session)
                answer = json.loads(await socket.receive_text(timeout=5))
                assert answer["data"]["status"] == 409


async def test_stuck_connection_keeps_its_place(
    wired: AsyncClient, account: Account, issued: Issued, monkeypatch: pytest.MonkeyPatch
) -> None:
    """One that takes no close still counts, until its TCP ends."""
    stuck = asyncio.Event()

    async def never(*_: object) -> None:
        """Wait as Uvicorn does on a client that stopped reading."""
        stuck.set()
        await asyncio.Event().wait()

    monkeypatch.setattr(WebSocket, "close", never)
    async with aconnect_ws(URL, wired, headers=bearer(issued)) as socket:
        await socket.send_bytes(b"{}")
        await asyncio.wait_for(stuck.wait(), 5)
        await socket.send_text("{")
        await asyncio.sleep(0.2)
        assert await places(account.id) == 1
    await asyncio.sleep(0.2)
    assert await places(account.id) == 0


async def test_connection_holds_no_transaction(wired: AsyncClient, issued: Issued) -> None:
    """Each session to the database ends with its read."""
    opened: set[SessionTransaction] = set()
    begun = 0

    def begins(_: Session, transaction: SessionTransaction) -> None:
        """Keep the transaction of a session."""
        nonlocal begun
        begun += 1
        opened.add(transaction)

    def ends(_: Session, transaction: SessionTransaction) -> None:
        """Forget the transaction that ended."""
        opened.discard(transaction)

    event.listen(Session, "after_transaction_create", begins)
    event.listen(Session, "after_transaction_end", ends)
    try:
        async with aconnect_ws(URL, wired, headers=bearer(issued)) as socket:
            assert await alive(socket)
            assert begun > 0
            assert opened == set()
    finally:
        event.remove(Session, "after_transaction_create", begins)
        event.remove(Session, "after_transaction_end", ends)


def test_messages_are_in_the_openapi() -> None:
    """The clients generate them like any other model."""
    schemas = app.openapi()["components"]["schemas"]
    assert schemas["AccessTokenMessage"]["additionalProperties"] is False
    assert set(schemas["ErrorMessage"]["properties"]) == {"type", "data"}
    # One schema: a generator merges a union and requires its errors.
    assert schemas["ErrorMessage"]["properties"]["data"] == {
        "$ref": "#/components/schemas/MessageProblem"
    }
    assert "errors" not in schemas["MessageProblem"]["required"]
    assert "additionalProperties" not in schemas["MessageProblem"]
