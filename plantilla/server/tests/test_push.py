"""The push: its registration, what it carries and how it is sent."""

import asyncio
import base64
import json
import threading
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import parse_qs
from uuid import UUID, uuid4

import firebase_admin
import pytest
import sqlalchemy as sa
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from fastapi import FastAPI
from firebase_admin import exceptions, messaging
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import errors, main, push, tasks
from app.config import settings
from app.enums import Push, Role
from app.main import api_router
from app.methods import METHODS
from app.models.account.account import Account
from app.models.account.account_session import AccountSession
from app.models.account.push_fid import PushFid
from app.models.account.push_subscription import PushSubscription
from app.routers import fcm as fcm_router
from app.routers import web_push as web_push_router
from app.services import account as account_service
from app.services import accounts, fcm, messages, notices, sessions, web_push
from app.services import push as push_service
from app.services.fcm import Content
from app.services.sessions import Client, Principal

CLIENT = Client("127.0.0.1", "test")
# The services fixture replaces them.
SEND, READ, START = messaging.send_each_async, fcm.credential, fcm.app
FID = "cAAAAAAAAAAAAAAAAAAAAA"
OTHER_FID = "dBBBBBBBBBBBBBBBBBBBBB"
ENDPOINT = "https://push.example.com/send/abc"
CONTENT = Content("Título", "Texto", "/lugar", "canal", timedelta(days=2))
needs_fcm = pytest.mark.skipif(Push.FCM not in push.PUSH, reason="the product has no FCM")
needs_web = pytest.mark.skipif(Push.WEB not in push.PUSH, reason="the product has no Web Push")
needs_both = pytest.mark.skipif(len(push.PUSH) < 2, reason="the product lacks one")


def b64(value: bytes) -> str:
    """Write base64url without padding."""
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def unb64(value: str) -> bytes:
    """Read base64url without padding."""
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def point(key: ec.EllipticCurvePublicKey) -> bytes:
    """Write a public key as an uncompressed point."""
    return key.public_bytes(
        serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint
    )


BROWSER = ec.generate_private_key(ec.SECP256R1())
SECRET = bytes(range(16))
COMPRESSED = BROWSER.public_key().public_bytes(
    serialization.Encoding.X962, serialization.PublicFormat.CompressedPoint
)
KEYS = {"p256dh": b64(point(BROWSER.public_key())), "auth": b64(SECRET)}


def subscription(endpoint: str = ENDPOINT, **keys: str) -> dict[str, Any]:
    """Write a subscription as toJSON() does."""
    return {"endpoint": endpoint, "expirationTime": None, "keys": {**KEYS, **keys}}


@dataclass
class Credential:
    """The service account, whose token expired."""

    valid: bool = False
    renewed_in: list[threading.Thread] = field(default_factory=list)

    def renew(self) -> None:
        """Renew the token, where it is called."""
        self.renewed_in.append(threading.current_thread())
        self.valid = True


@dataclass
class Firebase:
    """The app of Firebase of the tests."""


@dataclass
class Services:
    """What the services of push received, and what they answer."""

    firebase: Firebase = field(default_factory=Firebase)
    credential: Credential = field(default_factory=Credential)
    batches: list[list[dict[str, Any]]] = field(default_factory=list)
    posts: list[tuple[str, dict[str, str], bytes]] = field(default_factory=list)
    error: Exception | None = None
    status: int = 201

    @property
    def fids(self) -> set[str]:
        """Return where FCM sent."""
        return {message["fid"] for batch in self.batches for message in batch}

    @property
    def endpoints(self) -> set[str]:
        """Return where Web Push sent."""
        return {url for url, _, _ in self.posts}


@pytest.fixture(autouse=True)
def services(monkeypatch: pytest.MonkeyPatch) -> Services:
    """Keep each push: no test sends one."""
    found = Services()

    async def send_each_async(batch: list[messaging.Message], app: Firebase) -> Any:
        """Answer as FCM."""
        assert app is found.firebase
        found.batches.append([json.loads(str(message)) for message in batch])
        response = {"name": "1"} if found.error is None else None
        return messaging.BatchResponse(
            [messaging.SendResponse(response, found.error) for _ in batch]
        )

    async def post(url: str, headers: dict[str, str], body: bytes) -> int:
        """Answer as a push service."""
        found.posts.append((url, headers, body))
        return found.status

    monkeypatch.setattr(fcm, "app", lambda: found.firebase)
    monkeypatch.setattr(fcm, "credential", lambda: found.credential)
    monkeypatch.setattr(messaging, "send_each_async", send_each_async)
    monkeypatch.setattr(web_push.client, "post", post)
    return found


@pytest.fixture
async def account(session: AsyncSession) -> Account:
    """Create an account."""
    row = Account(email="ana@example.com", role=Role.USER, language="es")
    session.add(row)
    await session.flush()
    return row


async def opened(session: AsyncSession, account: Account) -> tuple[UUID, dict[str, str]]:
    """Open an app session; return its ID and its header."""
    issued = await sessions.open_app(session, account, CLIENT, "es")
    await session.flush()
    return issued.session_id, {"Authorization": f"Bearer {issued.access_token}"}


async def browsed(session: AsyncSession, account: Account) -> tuple[UUID, dict[str, str]]:
    """Open a web session; return its ID and its headers."""
    token, session_id = await sessions.open_web(session, account, CLIENT, "es")
    await session.flush()
    return session_id, {"Cookie": f"{sessions.COOKIE}={token}", "Origin": "https://test"}


async def devices(session: AsyncSession, account: Account) -> tuple[UUID, UUID]:
    """Give the account an app and a browser, in their sessions."""
    app_id, _ = await opened(session, account)
    web_id, _ = await browsed(session, account)
    session.add(PushFid(session_id=app_id, fid=FID, language="es"))
    session.add(PushSubscription(session_id=web_id, endpoint=ENDPOINT, language="es", **KEYS))
    await session.flush()
    return app_id, web_id


async def rows(session: AsyncSession, model: type[Any]) -> list[dict[str, Any]]:
    """Return each row of a table, as the database has it."""
    found = await session.execute(sa.select(model.__table__))
    return [dict(row) for row in found.mappings()]


def echo(header: str) -> str:
    """Choose the language as it was asked."""
    return header


def anywhere(_: str) -> bool:
    """Let the tests reach their own machine."""
    return True


def render(language: str) -> Content:
    """Write a push whose title is its language."""
    return Content(language, "Texto", "/lugar", "canal", timedelta(days=2))


async def sent(session: AsyncSession, account: Account) -> None:
    """Push to the account, and send as after the commit."""
    await push_service.later(session, account.id, render)
    await messages.flush(session)


@needs_fcm
async def test_app_registers_its_fid(
    client: AsyncClient, session: AsyncSession, account: Account, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With the language asked, and again without a second row."""
    monkeypatch.setattr(fcm_router, "language", echo)
    session_id, headers = await opened(session, account)
    for asked in ("es", "en", "en"):
        response = await client.put(
            "/api/account/push/fid",
            json={"fid": FID},
            headers={**headers, "Accept-Language": asked},
        )
        assert response.status_code == 204
        assert await rows(session, PushFid) == [
            {"session_id": session_id, "fid": FID, "language": asked}
        ]


@needs_web
async def test_web_registers_its_subscription(
    client: AsyncClient, session: AsyncSession, account: Account, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With the language asked, and again without a second row."""
    monkeypatch.setattr(web_push_router, "language", echo)
    session_id, headers = await browsed(session, account)
    for asked in ("es", "en", "en"):
        response = await client.put(
            "/api/account/push/subscription",
            json=subscription(),
            headers={**headers, "Accept-Language": asked},
        )
        assert response.status_code == 204
        assert await rows(session, PushSubscription) == [
            {"session_id": session_id, "endpoint": ENDPOINT, "language": asked, **KEYS}
        ]


@needs_both
async def test_registering_replaces_the_one_of_the_session(
    client: AsyncClient, session: AsyncSession, account: Account
) -> None:
    """A session has one device."""
    app_id, app = await opened(session, account)
    web_id, web = await browsed(session, account)
    other = f"{ENDPOINT}/2"
    for fid in (FID, OTHER_FID):
        await client.put("/api/account/push/fid", json={"fid": fid}, headers=app)
    for endpoint in (ENDPOINT, other):
        await client.put(
            "/api/account/push/subscription", json=subscription(endpoint), headers=web
        )
    assert [(r["session_id"], r["fid"]) for r in await rows(session, PushFid)] == [
        (app_id, OTHER_FID)
    ]
    assert [(r["session_id"], r["endpoint"]) for r in await rows(session, PushSubscription)] == [
        (web_id, other)
    ]


@needs_both
async def test_device_of_another_session_passes_to_the_new_one(
    client: AsyncClient, session: AsyncSession, account: Account
) -> None:
    """The device has another session, even of another account."""
    await devices(session, account)
    other = Account(email="bea@example.com", role=Role.USER, language="es")
    session.add(other)
    await session.flush()
    app_id, app = await opened(session, other)
    web_id, web = await browsed(session, other)
    assert (
        await client.put("/api/account/push/fid", json={"fid": FID}, headers=app)
    ).status_code == 204
    assert (
        await client.put("/api/account/push/subscription", json=subscription(), headers=web)
    ).status_code == 204
    assert [r["session_id"] for r in await rows(session, PushFid)] == [app_id]
    assert [r["session_id"] for r in await rows(session, PushSubscription)] == [web_id]


@needs_both
async def test_session_of_the_other_form_is_a_403(
    client: AsyncClient, session: AsyncSession, account: Account
) -> None:
    """An app has no subscription, and the web no FID."""
    _, app = await opened(session, account)
    _, web = await browsed(session, account)
    fid = await client.put("/api/account/push/fid", json={"fid": FID}, headers=web)
    assert fid.status_code == 403
    other = await client.put("/api/account/push/subscription", json=subscription(), headers=app)
    assert other.status_code == 403
    assert await rows(session, PushFid) == []
    assert await rows(session, PushSubscription) == []


@needs_fcm
@pytest.mark.parametrize("fid", ["", FID[:-1], FID + "A", FID[:-1] + "/"])
async def test_fid_that_is_none_is_a_422(
    client: AsyncClient, session: AsyncSession, account: Account, fid: str
) -> None:
    """A FID has 22 characters of base64url."""
    _, headers = await opened(session, account)
    response = await client.put("/api/account/push/fid", json={"fid": fid}, headers=headers)
    assert response.status_code == 422
    assert response.json()["errors"][0]["pointer"] == "/fid"


@needs_web
@pytest.mark.parametrize(
    ("change", "pointer"),
    [
        ({"endpoint": "http://push.example.com/a"}, "/endpoint"),
        ({"endpoint": "https:///a"}, "/endpoint"),
        ({"endpoint": "https://push.example.com:99999/a"}, "/endpoint"),
        ({"endpoint": "https://push.example.com/á"}, "/endpoint"),
        ({"endpoint": "https://push.example.com/" + "a" * 2048}, "/endpoint"),
        ({"p256dh": b64(b"\x04" + bytes(64))}, "/keys/p256dh"),
        ({"p256dh": b64(point(BROWSER.public_key())[:64])}, "/keys/p256dh"),
        ({"p256dh": "A" * 85}, "/keys/p256dh"),
        ({"p256dh": b64(COMPRESSED)}, "/keys/p256dh"),
        ({"auth": b64(SECRET[:15])}, "/keys/auth"),
        ({"auth": b64(SECRET + b"A")}, "/keys/auth"),
    ],
)
async def test_subscription_that_is_none_is_a_422(
    client: AsyncClient,
    session: AsyncSession,
    account: Account,
    change: dict[str, str],
    pointer: str,
) -> None:
    """An endpoint that is not https, or keys that do not encrypt."""
    _, headers = await browsed(session, account)
    response = await client.put(
        "/api/account/push/subscription", json=subscription(**change), headers=headers
    )
    assert response.status_code == 422
    assert [error["pointer"] for error in response.json()["errors"]] == [pointer]


@needs_web
async def test_endpoint_of_2048_characters_is_taken(
    client: AsyncClient, session: AsyncSession, account: Account
) -> None:
    """It fits in the index."""
    _, headers = await browsed(session, account)
    long = (ENDPOINT + "".join(uuid4().hex for _ in range(70)))[:2048]
    response = await client.put(
        "/api/account/push/subscription", json=subscription(long), headers=headers
    )
    assert response.status_code == 204


@needs_web
async def test_key_is_the_public_one_of_vapid(
    client: AsyncClient, session: AsyncSession, account: Account
) -> None:
    """The web asks for it with its session."""
    assert (await client.get("/api/account/push/key")).status_code == 401
    _, headers = await browsed(session, account)
    key = (await client.get("/api/account/push/key", headers=headers)).json()["key"]
    number = int.from_bytes(unb64(settings.vapid_key))
    assert unb64(key) == point(ec.derive_private_key(number, ec.SECP256R1()).public_key())


@pytest.mark.usefixtures("database")
async def test_service_the_product_does_not_use_has_no_routes() -> None:
    """None of them, without a service."""
    probe = FastAPI()
    errors.install(probe)
    probe.include_router(api_router(METHODS, frozenset()))
    async with AsyncClient(transport=ASGITransport(app=probe), base_url="http://test") as client:
        assert (await client.put("/api/account/push/fid")).status_code == 404
        assert (await client.put("/api/account/push/subscription")).status_code == 404
        assert (await client.get("/api/account/push/key")).status_code == 404


@pytest.mark.parametrize("used", [frozenset(), frozenset({Push.FCM}), frozenset({Push.WEB})])
async def test_push_goes_only_through_the_services_of_the_product(
    session: AsyncSession,
    account: Account,
    services: Services,
    monkeypatch: pytest.MonkeyPatch,
    used: frozenset[Push],
) -> None:
    """A service that is not declared receives nothing."""
    await devices(session, account)
    monkeypatch.setattr(push, "PUSH", used)
    await sent(session, account)
    assert services.fids == ({FID} if Push.FCM in used else set())
    assert services.endpoints == ({ENDPOINT} if Push.WEB in used else set())


@needs_both
async def test_push_goes_to_the_live_sessions_of_the_account(
    session: AsyncSession, account: Account, services: Services
) -> None:
    """Not to one past its 30 days, nor to another account."""
    await devices(session, account)
    stale, _ = await opened(session, account)
    session.add(PushFid(session_id=stale, fid=OTHER_FID, language="es"))
    await session.execute(
        sa.update(AccountSession)
        .where(AccountSession.id == stale)
        .values(last_used_at=datetime.now(UTC) - sessions.IDLE - timedelta(minutes=1))
    )
    other = Account(email="bea@example.com", role=Role.USER, language="es")
    session.add(other)
    await session.flush()
    web_id, _ = await browsed(session, other)
    session.add(
        PushSubscription(session_id=web_id, endpoint=f"{ENDPOINT}/bea", language="es", **KEYS)
    )
    await sent(session, account)
    assert services.fids == {FID}
    assert services.endpoints == {ENDPOINT}


@needs_both
async def test_session_that_ends_forgets_its_device(
    session: AsyncSession, account: Account
) -> None:
    """Its FID and its subscription go with it."""
    await devices(session, account)
    await sessions.drop(session, AccountSession.account_id == account.id)
    assert await rows(session, PushFid) == []
    assert await rows(session, PushSubscription) == []


@needs_both
async def test_push_goes_in_the_language_of_the_device(
    session: AsyncSession, account: Account, services: Services
) -> None:
    """Each device has its own."""
    await devices(session, account)
    await session.execute(sa.update(PushFid).values(language="en"))
    await session.execute(sa.update(PushSubscription).values(language="pt"))
    await sent(session, account)
    assert services.batches[0][0]["notification"]["title"] == "en"
    assert json.loads(decrypt(services.posts[0][2]))["notification"]["title"] == "pt"


@needs_fcm
async def test_fcm_message_names_its_channel_its_route_and_its_expiry(
    session: AsyncSession, account: Account, services: Services
) -> None:
    """On Android and on iOS."""
    await devices(session, account)
    await sent(session, account)
    ((message,),) = services.batches
    expiry = int(message["apns"]["headers"].pop("apns-expiration"))
    assert abs(expiry - time.time() - timedelta(days=2).total_seconds()) < 60
    assert message == {
        "fid": FID,
        "notification": {"title": "es", "body": "Texto"},
        "data": {"navigate": "/lugar"},
        "android": {"ttl": "172800s", "notification": {"channel_id": "canal"}},
        "apns": {"headers": {}},
    }


@needs_fcm
async def test_fcm_takes_500_messages_at_once(services: Services) -> None:
    """A longer list goes in batches."""
    to = fcm.Installation(uuid4(), FID, "es")
    await fcm.send([(to, CONTENT)] * 501)
    assert [len(batch) for batch in services.batches] == [500, 1]


@needs_fcm
async def test_token_of_google_is_renewed_in_a_thread(services: Services) -> None:
    """Once, before sending: the SDK renews it blocking the loop."""
    to = fcm.Installation(uuid4(), FID, "es")
    await fcm.send([(to, CONTENT)])
    await fcm.send([(to, CONTENT)])
    (renewed_in,) = services.credential.renewed_in
    assert renewed_in is not threading.main_thread()
    assert len(services.batches) == 2


@dataclass
class Google:
    """The token endpoint and FCM, which refuses each message."""

    tokens: list[str] = field(default_factory=list)
    sent: list[str] = field(default_factory=list)

    async def serve(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Answer a request and close."""
        head = (await reader.readuntil(b"\r\n\r\n")).decode()
        headers = dict(line.lower().split(": ", 1) for line in head.split("\r\n")[1:-2])
        body = await reader.readexactly(int(headers["content-length"]))
        answer: dict[str, Any] = {"error": {"status": "UNAUTHENTICATED"}}
        status = 401
        if head.startswith("POST /token "):
            claims = parse_qs(body.decode())["assertion"][0].split(".")[1]
            self.tokens.append(json.loads(unb64(claims))["scope"])
            answer = {"access_token": "new", "expires_in": 3600}
            status = 200
        else:
            self.sent.append(headers["authorization"])
        text = json.dumps(answer)
        writer.write(
            f"HTTP/1.1 {status} X\r\nContent-Type: application/json\r\n"
            f"Content-Length: {len(text)}\r\nConnection: close\r\n\r\n{text}".encode()
        )
        await writer.drain()
        writer.close()


@pytest.fixture
async def google(monkeypatch: pytest.MonkeyPatch) -> AsyncIterator[Google]:
    """Serve Google, to the service account of the deployment."""
    found = Google()
    listening = await asyncio.start_server(found.serve, "127.0.0.1", 0)
    url = f"http://127.0.0.1:{listening.sockets[0].getsockname()[1]}"
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048).private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    info = {
        "type": "service_account",
        "project_id": "test",
        "private_key": key.decode(),
        "client_email": "test@example.com",
        "token_uri": f"{url}/token",
    }
    monkeypatch.setattr(settings, "firebase_credentials", info)
    credential = READ.__wrapped__()
    monkeypatch.setattr(fcm, "credential", lambda: credential)
    firebase = START.__wrapped__()
    monkeypatch.setattr(fcm, "app", lambda: firebase)
    monkeypatch.setattr(messaging, "send_each_async", SEND)
    monkeypatch.setattr(messaging._MessagingService, "FCM_URL", f"{url}/{{0}}/send")
    yield found
    # It closes its client with a loop of its own.
    await asyncio.to_thread(firebase_admin.delete_app, firebase)
    listening.close()
    await listening.wait_closed()


@needs_fcm
async def test_token_of_google_is_only_for_fcm(google: Google) -> None:
    """The service account may do more."""
    await asyncio.to_thread(fcm.credential().renew)
    assert fcm.credential().valid
    assert google.tokens == ["https://www.googleapis.com/auth/firebase.messaging"]


@needs_fcm
async def test_token_of_google_stays_while_it_sends(
    google: Google, caplog: pytest.LogCaptureFixture
) -> None:
    """A 401 renews nothing, and each message has its answer."""
    to = [fcm.Installation(uuid4(), FID, "es") for _ in range(3)]
    await fcm.send([(one, CONTENT) for one in to])
    assert len(google.tokens) == 1
    assert set(google.sent) == {"bearer new"}
    for one in to:
        assert f"the session {one.session_id}: UnauthenticatedError" in caplog.text
    # Nor does one that expires meanwhile.
    fcm.credential().expiry = datetime.now(UTC).replace(tzinfo=None)
    await messaging.send_each_async([fcm.message(to[0], CONTENT)], app=fcm.app())
    assert len(google.tokens) == 1


def decrypt(body: bytes) -> bytes:
    """Read an aes128gcm message as the browser, by RFC 8291."""
    salt, size = body[:16], body[20]
    sender, sealed = body[21 : 21 + size], body[21 + size :]
    shared = BROWSER.exchange(
        ec.ECDH(), ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), sender)
    )

    def derive(secret: bytes, salt: bytes, info: bytes, length: int) -> bytes:
        """Derive a key with HKDF."""
        return HKDF(hashes.SHA256(), length, salt, info).derive(secret)

    info = b"WebPush: info\x00" + point(BROWSER.public_key()) + sender
    key = derive(shared, SECRET, info, 32)
    content_key = derive(key, salt, b"Content-Encoding: aes128gcm\x00", 16)
    nonce = derive(key, salt, b"Content-Encoding: nonce\x00", 12)
    return AESGCM(content_key).decrypt(nonce, sealed, None).rstrip(b"\x00")[:-1]


def claims(header: str) -> dict[str, Any]:
    """Verify the JWT of VAPID by RFC 8292, and read its claims."""
    token, key = header.removeprefix("vapid t=").split(",k=")
    signed, _, signature = token.rpartition(".")
    raw = unb64(signature)
    der = encode_dss_signature(int.from_bytes(raw[:32]), int.from_bytes(raw[32:]))
    public = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), unb64(key))
    public.verify(der, signed.encode(), ec.ECDSA(hashes.SHA256()))
    assert key == web_push.PUBLIC_KEY
    first, second = signed.split(".")
    assert json.loads(unb64(first))["alg"] == "ES256"
    found: dict[str, Any] = json.loads(unb64(second))
    return found


@needs_web
async def test_web_push_is_a_declarative_message_encrypted_and_signed(
    session: AsyncSession, account: Account, services: Services
) -> None:
    """Only the browser reads it, and VAPID says who sends it."""
    await devices(session, account)
    await sent(session, account)
    ((url, headers, body),) = services.posts
    assert url == ENDPOINT
    assert headers["TTL"] == str(2 * 24 * 60 * 60)
    assert headers["Content-Encoding"] == "aes128gcm"
    assert json.loads(decrypt(body)) == {
        "web_push": 8030,
        "notification": {"title": "es", "body": "Texto", "navigate": "/lugar"},
    }
    found = claims(headers["Authorization"])
    assert found["aud"] == "https://push.example.com"
    assert found["sub"] == f"mailto:{settings.contact}"
    assert abs(found["exp"] - time.time() - 12 * 60 * 60) < 60
    with pytest.raises(InvalidSignature):
        claims(headers["Authorization"].replace("t=e", "t=f", 1))


@needs_both
@pytest.mark.parametrize("status", [404, 410])
async def test_device_that_no_longer_receives_is_deleted(
    session: AsyncSession, account: Account, services: Services, status: int
) -> None:
    """FCM says UNREGISTERED, and a push service 404 or 410."""
    await devices(session, account)
    services.error = messaging.UnregisteredError("NotRegistered")
    services.status = status
    await sent(session, account)
    assert await rows(session, PushFid) == []
    assert await rows(session, PushSubscription) == []


@needs_both
async def test_device_that_registered_again_meanwhile_stays(
    session: AsyncSession, account: Account, services: Services
) -> None:
    """Only what the service refused is deleted."""
    await devices(session, account)
    await push_service.later(session, account.id, render)
    await session.execute(sa.update(PushFid).values(fid=OTHER_FID))
    await session.execute(sa.update(PushSubscription).values(endpoint=f"{ENDPOINT}/2"))
    services.error = messaging.UnregisteredError("NotRegistered")
    services.status = 410
    await messages.flush(session)
    assert [row["fid"] for row in await rows(session, PushFid)] == [OTHER_FID]
    assert [r["endpoint"] for r in await rows(session, PushSubscription)] == [f"{ENDPOINT}/2"]


@needs_both
@pytest.mark.parametrize("status", [199, 302, 413, 429, 500, 999])
async def test_push_that_fails_goes_to_the_log_and_the_device_stays(
    session: AsyncSession,
    account: Account,
    services: Services,
    caplog: pytest.LogCaptureFixture,
    status: int,
) -> None:
    """With the session and the status, and nothing that sends to it."""
    app_id, web_id = await devices(session, account)
    services.error = exceptions.UnavailableError(f"{FID} unavailable")
    services.status = status
    await sent(session, account)
    assert f"{web_id}: {status}" in caplog.text
    assert f"{app_id}: UnavailableError" in caplog.text
    for secret in (FID, ENDPOINT, *KEYS.values()):
        assert secret not in caplog.text
    assert len(await rows(session, PushFid)) == 1
    assert len(await rows(session, PushSubscription)) == 1


@needs_both
async def test_push_that_breaks_does_not_fail_the_request(
    session: AsyncSession,
    account: Account,
    services: Services,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """An error of one service leaves the other, and the request."""
    _, web_id = await devices(session, account)

    def broken() -> Firebase:
        """Fail as a deployment without its credential."""
        raise ValueError(f"no credential for {ENDPOINT}")

    monkeypatch.setattr(fcm, "app", broken)
    await sent(session, account)
    assert services.endpoints == {ENDPOINT}
    assert "A push did not reach FCM: ValueError" in caplog.text

    async def refuse(url: str, headers: dict[str, str], body: bytes) -> int:
        """Fail as an endpoint that does not open."""
        raise OSError(url)

    monkeypatch.setattr(web_push.client, "post", refuse)
    await sent(session, account)
    assert f"A push did not reach the session {web_id}: OSError" in caplog.text
    assert ENDPOINT not in caplog.text


@needs_web
async def test_pushes_go_at_once_and_wait_a_little(
    session: AsyncSession,
    account: Account,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Endpoints that do not answer hold the request only that."""
    for number in range(5):
        web_id, _ = await browsed(session, account)
        session.add(
            PushSubscription(
                session_id=web_id, endpoint=f"{ENDPOINT}/{number}", language="es", **KEYS
            )
        )
    await session.flush()
    monkeypatch.setattr(push_service, "WAIT", timedelta(seconds=0.2))

    async def hang(url: str, headers: dict[str, str], body: bytes) -> int:
        """Never answer."""
        await asyncio.sleep(30)
        return 201

    monkeypatch.setattr(web_push.client, "post", hang)
    start = time.monotonic()
    await sent(session, account)
    assert time.monotonic() - start < 0.8
    assert caplog.text.count("TimeoutError") == 5


def test_push_waits_5_seconds() -> None:
    """The wait of fastapi.md."""
    assert timedelta(seconds=5) == push_service.WAIT


@needs_both
async def test_notice_reaches_every_device(
    client: AsyncClient, session: AsyncSession, account: Account, services: Services
) -> None:
    """The one that made the change too, as the email says it."""
    _, web_id = await devices(session, account)
    row = await session.get_one(AccountSession, web_id)
    await account_service.erase(session, account, CLIENT, account)
    await messages.flush(session)
    assert row.account_id == account.id
    ((message,),) = services.batches
    assert message["notification"]["title"] == "Se borró tu cuenta"
    assert settings.contact in message["notification"]["body"]
    assert message["data"] == {"navigate": "/account"}
    assert message["android"] == {
        "ttl": f"{28 * 24 * 60 * 60}s",
        "notification": {"channel_id": "security"},
    }
    ((url, headers, body),) = services.posts
    assert url == ENDPOINT
    assert headers["TTL"] == str(28 * 24 * 60 * 60)
    assert json.loads(decrypt(body))["notification"] == {
        **message["notification"],
        "navigate": "/account",
    }


@needs_both
async def test_disabled_account_hears_it_on_the_devices_it_loses(
    session: AsyncSession, account: Account, services: Services
) -> None:
    """Its sessions end in the same transaction."""
    await devices(session, account)
    boss = Account(email="dueno@example.com", role=Role.SUPERADMIN, language="es")
    session.add(boss)
    await session.flush()
    boss_id, _ = await opened(session, boss)
    principal = Principal(boss, await session.get_one(AccountSession, boss_id))
    await accounts.disable(session, principal, account, CLIENT)
    await messages.flush(session)
    assert await rows(session, PushFid) == []
    assert services.fids == {FID}
    assert services.endpoints == {ENDPOINT}


async def test_content_of_a_notice_is_its_email() -> None:
    """In its language, with the name of the passkey."""
    found = notices.content("es", notices.Notice.PASSKEY_LINKED, "Teléfono")
    assert found.title == "Se agregó una passkey a tu cuenta"
    assert "Teléfono" in found.body
    assert settings.contact in found.body


@pytest.mark.parametrize(
    ("host", "expected"),
    [
        ("93.184.215.14", True),
        ("2606:2800:21f:cb07:6820:80da:af6b:8b2c", True),
        ("127.0.0.1", False),
        ("10.0.0.1", False),
        ("172.16.0.1", False),
        ("192.168.1.1", False),
        ("100.64.0.1", False),
        ("169.254.169.254", False),
        ("0.0.0.0", False),
        ("::1", False),
        ("::ffff:127.0.0.1", False),
        ("fd00::1", False),
        ("fe80::1%eth0", False),
    ],
)
def test_only_a_global_address_is_public(host: str, expected: bool) -> None:
    """Not the network of the server, its machine or its metadata."""
    assert web_push.is_global(host) is expected


class Server:
    """A server of the machine that answers as each test says."""

    def __init__(self) -> None:
        """Start without requests."""
        self.lines: list[str] = []
        self.heads: list[str] = []
        self.answer = b"HTTP/1.1 201 Created\r\nConnection: close\r\nContent-Length: 0\r\n\r\n"
        self.port = 0

    async def serve(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Keep the request, and answer."""
        head = (await reader.readuntil(b"\r\n\r\n")).decode()
        self.lines.append(head.split("\r\n")[0])
        self.heads.append(head.lower())
        writer.write(self.answer)
        await writer.drain()
        await reader.read()
        writer.close()


@pytest.fixture
async def server() -> AsyncIterator[Server]:
    """Listen on the machine."""
    found = Server()
    listening = await asyncio.start_server(found.serve, "127.0.0.1", 0)
    found.port = listening.sockets[0].getsockname()[1]
    yield found
    listening.close()


@pytest.fixture
async def browser() -> AsyncIterator[web_push.Client]:
    """Open a client of its own, which posts."""
    client = web_push.Client()
    yield client
    await client.aclose()


@pytest.mark.parametrize("host", ["127.0.0.1", "localhost"])
async def test_endpoint_does_not_reach_the_machine(
    server: Server, browser: web_push.Client, host: str
) -> None:
    """By its address or by a name that resolves to it."""
    with pytest.raises(OSError, match="Cannot connect"):
        await browser.post(f"http://{host}:{server.port}/", {}, b"x")
    assert server.lines == []


async def test_redirection_is_not_followed_and_the_body_is_not_read(
    server: Server, browser: web_push.Client, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A body that never ends does not hold the push."""
    monkeypatch.setattr(web_push, "is_global", anywhere)
    server.answer = (
        b"HTTP/1.1 307 Temporary Redirect\r\nLocation: /internal\r\n"
        b"Set-Cookie: a=b\r\nContent-Length: 1000000000\r\n\r\n"
    )
    async with asyncio.timeout(5):
        status = await browser.post(f"http://localhost:{server.port}/send", {"TTL": "1"}, b"x")
    assert status == 307
    assert server.lines == ["POST /send HTTP/1.1"]
    server.answer = b"HTTP/1.1 201 Created\r\nContent-Length: 1000000000\r\n\r\n"
    async with asyncio.timeout(5):
        assert await browser.post(f"http://localhost:{server.port}/send", {}, b"x") == 201
    assert "cookie" not in server.heads[1]


async def test_lifespan_and_tasks_close_the_client(monkeypatch: pytest.MonkeyPatch) -> None:
    """A process that ends leaves no session open."""
    closed: list[str] = []

    class Pool:
        """A pool that closes nothing."""

        async def dispose(self) -> None:
            """Keep the pool of the tests."""

        async def aclose(self) -> None:
            """Keep the connections of the tests."""

    class Counted(web_push.Client):
        """A client that counts its closings."""

        async def aclose(self) -> None:
            """Count it."""
            closed.append("client")

    async def nothing(*_: object) -> None:
        """Do nothing."""

    monkeypatch.setattr(web_push, "client", Counted())
    monkeypatch.setattr(main, "engine", Pool())
    monkeypatch.setattr(main.store, "client", Pool())
    monkeypatch.setattr(main.events, "record", nothing)
    async with main.lifespan(main.app):
        pass
    assert closed == ["client"]
    monkeypatch.setattr(tasks, "engine", Pool())
    monkeypatch.setitem(tasks.TASKS, "sweep", nothing)
    await tasks.run("sweep")
    assert closed == ["client", "client"]


async def test_client_opens_one_session_and_closes_it(
    server: Server, browser: web_push.Client, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Every push goes by the same one."""
    monkeypatch.setattr(web_push, "is_global", anywhere)
    await browser.post(f"http://localhost:{server.port}/", {}, b"x")
    first = browser.http
    await browser.post(f"http://localhost:{server.port}/", {}, b"x")
    assert first is not None
    assert browser.http is first
    await browser.aclose()
    assert first.closed
    assert browser.http is None
