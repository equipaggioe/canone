"""Registering an account: its code, its first passkey and its role."""

import json
import re
from datetime import UTC, datetime, timedelta
from http.cookies import SimpleCookie
from typing import Any

import httpx
import pytest
import sqlalchemy as sa
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession
from webauthn.helpers import base64url_to_bytes

from app import errors, store
from app.config import settings
from app.enums import Method, Role
from app.methods import METHODS
from app.models.account.account import Account
from app.models.account.passkey import Passkey
from app.models.event.event_log import EventLog
from app.services import attestation, codes, events, limits, sessions
from tests.authenticator import UP, Authenticator

EMAIL = "bea@example.com"
PHONE = "+56221234567"
HOST = f"app.{settings.domain}"
ANDROID = "test-android"
# A test that registers a passkey needs the method.
needs_passkey = pytest.mark.skipif(
    Method.PASSKEY not in METHODS, reason="the product offers no passkey"
)


@pytest.fixture
def recorded(monkeypatch: pytest.MonkeyPatch) -> list[EventLog]:
    """Collect the events written in their own transaction.

    In a test that transaction is a savepoint of the request, and a
    request that fails would undo it.
    """
    found: list[EventLog] = []

    async def record(row: EventLog) -> None:
        """Keep the event."""
        found.append(row)

    monkeypatch.setattr(events, "record", record)
    return found


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> list[int]:
    """Move the time of the rate limits by hand, in milliseconds."""
    moment = [limits.now()]
    monkeypatch.setattr(limits, "now", lambda: moment[0])
    return moment


def body(request: httpx.Request) -> dict[str, Any]:
    """Read the JSON a request sent to Equipaggio."""
    found: dict[str, Any] = json.loads(request.content)
    return found


def code_in(request: httpx.Request) -> str:
    """Read the code of an email or an SMS sent to Equipaggio."""
    sent = body(request)
    found = re.search(r"\d{6}", sent.get("text") or sent["body"])
    assert found is not None
    return found[0]


async def ask(
    client: AsyncClient, headers: dict[str, str] | None = None, **identifier: str
) -> Response:
    """Ask for the code of a new account."""
    return await client.post("/api/auth/register/code", json=identifier, headers=headers)


async def new_code(
    client: AsyncClient, sent: list[httpx.Request], clock: list[int], **identifier: str
) -> str:
    """Ask for a code an hour later, and read it from Equipaggio."""
    clock[0] += 3_700_000
    response = await ask(client, {"Host": HOST}, **identifier)
    assert response.status_code == 204
    return code_in(sent[-1])


async def options(client: AsyncClient, **identifier: str) -> dict[str, Any]:
    """Ask for the options of the passkey of a new account."""
    response = await client.post("/api/auth/register/options", json=identifier)
    assert response.status_code == 200
    found: dict[str, Any] = response.json()
    return found


async def register(
    client: AsyncClient,
    authenticator: Authenticator,
    code: str | None,
    form: str = "token",
    create: dict[str, Any] | None = None,
    **extra: object,
) -> Response:
    """Register an account by email with a new passkey.

    Without the code, the registration brings the setup code in extra.
    """
    challenge = (await options(client, email=EMAIL))["challenge"]
    credential = authenticator.create(challenge, **(create or {}))
    sent: dict[str, object] = {"email": EMAIL, "passkeyName": "Phone", "credential": credential}
    if code is not None:
        sent["code"] = code
    return await client.post(
        f"/api/auth/register/{form}", json={**sent, **extra}, headers={"Accept-Language": "es"}
    )


async def actions(session: AsyncSession) -> list[str]:
    """Return the actions of the events, in order."""
    return list(await session.scalars(sa.select(EventLog.action).order_by(EventLog.id)))


async def test_email_code_is_6_digits_for_10_minutes(
    client: AsyncClient, sent: list[httpx.Request], clock: list[int]
) -> None:
    """The code goes by email, with its text and its HTML, in lowercase.

    It lives 10 minutes in Valkey, and the email expires with it.
    """
    response = await ask(client, email="Bea@Example.COM")
    assert response.status_code == 204
    request = sent[-1]
    assert request.method == "PUT"
    assert re.fullmatch(r"/api/email/[0-9a-f-]{36}", request.url.path)
    assert request.url.host == "equipaggio.net"
    assert request.headers["authorization"] == f"Bearer {settings.equipaggio_key}"
    email = body(request)
    assert email["to"] == EMAIL
    assert email["subject"]
    assert email["text"]
    assert email["html"]
    assert code_in(request) in email["html"]
    expires = datetime.fromisoformat(email["expiresAt"]) - datetime.now(UTC)
    assert timedelta(minutes=9) < expires <= timedelta(minutes=10)
    ttl = await store.client.pttl(codes.key("register", EMAIL))
    assert 590_000 <= ttl <= 600_000


async def test_sms_code_binds_the_host_and_the_android_hash(
    client: AsyncClient,
    sent: list[httpx.Request],
    clock: list[int],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An Android app finds its hash in the second last line.

    The last line binds the code to the host of the request, which must
    be a surface of the domain.
    """
    monkeypatch.setitem(settings.sms_hashes, ANDROID, "FA+9qCX9VSu")
    agent = f"{ANDROID}/1.0.0"
    response = await ask(client, {"Host": HOST, "User-Agent": agent}, phone=PHONE)
    assert response.status_code == 204
    sms = body(sent[-1])
    assert re.fullmatch(r"/api/sms/[0-9a-f-]{36}", sent[-1].url.path)
    code = code_in(sent[-1])
    lines = sms["body"].split("\n")
    assert lines[-2:] == ["FA+9qCX9VSu", f"@{HOST} #{code}"]
    assert sms["to"] == PHONE
    await store.client.flushdb()
    response = await ask(client, {"Host": settings.domain, "User-Agent": "web"}, phone=PHONE)
    assert response.status_code == 204
    lines = body(sent[-1])["body"].split("\n")
    assert len(lines) == 2
    assert lines[-1] == f"@{settings.domain} #{code_in(sent[-1])}"
    await store.client.flushdb()
    assert (await ask(client, {"Host": "evil.example"}, phone=PHONE)).status_code == 400


async def test_phone_is_validated_with_phonenumbers(client: AsyncClient) -> None:
    """A number that phonenumbers does not take as valid is a 422."""
    assert (await ask(client, {"Host": HOST}, phone="+56912345678")).status_code == 422


@pytest.mark.usefixtures("database")
async def test_code_fails_on_the_third_attempt() -> None:
    """The third failed attempt invalidates the code."""
    code = await codes.issue("register", EMAIL)
    wrong = f"{(int(code) + 1) % 10**6:06d}"
    assert not await codes.take("register", EMAIL, wrong)
    assert await codes.take("register", EMAIL, code)
    code = await codes.issue("register", EMAIL)
    for _ in range(3):
        assert not await codes.take("register", EMAIL, wrong)
    assert not await codes.take("register", EMAIL, code)


@pytest.mark.usefixtures("database")
async def test_code_is_used_once_and_a_new_one_replaces_it() -> None:
    """A code is spent by its use, and a new one replaces the old."""
    old = await codes.issue("register", EMAIL)
    new = await codes.issue("register", EMAIL)
    if old != new:
        assert not await codes.take("register", EMAIL, old)
    assert await codes.take("register", EMAIL, new)
    assert not await codes.take("register", EMAIL, new)


async def test_email_gets_one_code_a_minute_and_five_an_hour(
    client: AsyncClient, clock: list[int], recorded: list[EventLog]
) -> None:
    """A code too soon is a 429 with the limit and when to retry."""
    assert (await ask(client, email=EMAIL)).status_code == 204
    response = await ask(client, email=EMAIL)
    assert response.status_code == 429
    assert response.json()["detail"] == "One code a minute to this email"
    assert 1 <= int(response.headers["retry-after"]) <= 60
    assert [row.action for row in recorded] == ["excess_rate_limit_exceeded"]
    for _ in range(4):
        clock[0] += 61_000
        assert (await ask(client, email=EMAIL)).status_code == 204
    clock[0] += 61_000
    response = await ask(client, email=EMAIL)
    assert response.json()["detail"] == "Five codes an hour to this email"
    clock[0] += 3_600_000
    assert (await ask(client, email=EMAIL)).status_code == 204


async def test_number_gets_one_sms_a_minute_five_an_hour_and_ten_a_day(
    client: AsyncClient, clock: list[int]
) -> None:
    """A number gets one SMS a minute, five an hour and ten a day."""

    async def send() -> Response:
        """Ask for a code to the phone."""
        return await ask(client, {"Host": HOST}, phone=PHONE)

    assert (await send()).status_code == 204
    assert (await send()).json()["detail"] == "One SMS a minute to this number"
    for _ in range(4):
        clock[0] += 61_000
        assert (await send()).status_code == 204
    clock[0] += 61_000
    assert (await send()).json()["detail"] == "Five SMS an hour to this number"
    clock[0] += 3_600_000
    for _ in range(5):
        assert (await send()).status_code == 204
        clock[0] += 61_000
    clock[0] += 3_600_000
    assert (await send()).json()["detail"] == "Ten SMS a day to this number"


async def test_ip_asks_ten_sms_an_hour(client: AsyncClient) -> None:
    """An IP asks for ten SMS an hour, to any numbers."""
    numbers = [f"+5622123{index:04d}" for index in range(11)]
    answers = [(await ask(client, {"Host": HOST}, phone=number)).status_code for number in numbers]
    assert answers == [204] * 10 + [429]


@needs_passkey
async def test_existing_account_is_a_409(
    client: AsyncClient, session: AsyncSession, sent: list[httpx.Request], clock: list[int]
) -> None:
    """The code and the registration answer 409 to an account."""
    code = await new_code(client, sent, clock, email=EMAIL)
    session.add(Account(email=EMAIL, role=Role.USER, language="es"))
    await session.flush()
    assert (await ask(client, email=EMAIL)).status_code == 409
    assert (await register(client, Authenticator(), code)).status_code == 409


async def test_ten_conflicts_block_the_ip_for_30_minutes(
    client: AsyncClient, session: AsyncSession, clock: list[int]
) -> None:
    """The tenth 409 to an IP in 15 minutes blocks it 30 minutes."""
    session.add(Account(email=EMAIL, role=Role.USER, language="es"))
    await session.flush()
    for _ in range(9):
        assert (await ask(client, email=EMAIL)).status_code == 409
    clock[0] += 15 * 60_000 + 1
    assert (await ask(client, email=EMAIL)).status_code == 409
    for _ in range(8):
        assert (await ask(client, email=EMAIL)).status_code == 409
    assert (await ask(client, email=EMAIL)).status_code == 409
    response = await ask(client, email="other@example.com")
    assert response.status_code == 429
    assert 1790 <= int(response.headers["retry-after"]) <= 1800


@needs_passkey
async def test_creation_options_ask_a_discoverable_passkey(client: AsyncClient) -> None:
    """The options of create() follow autenticacion.md, «Passkeys».

    The challenge is 16 bytes that live in Valkey 10 minutes, and the
    user handle 64 random bytes.
    """
    found = await options(client, email=EMAIL)
    assert set(found) == {
        "challenge",
        "rp",
        "user",
        "pubKeyCredParams",
        "authenticatorSelection",
        "attestation",
        "excludeCredentials",
    }
    assert found["rp"] == {"id": settings.domain, "name": settings.domain}
    assert (found["user"]["name"], found["user"]["displayName"]) == (EMAIL, "")
    assert len(base64url_to_bytes(found["user"]["id"])) == 64
    assert [param["alg"] for param in found["pubKeyCredParams"]] == [-8, -7, -257]
    assert found["authenticatorSelection"] == {
        "residentKey": "required",
        "requireResidentKey": True,
        "userVerification": "preferred",
    }
    assert (found["attestation"], found["excludeCredentials"]) == ("none", [])
    raw = base64url_to_bytes(found["challenge"])
    assert len(raw) == 16
    assert 590 <= await store.client.ttl(attestation.creation_key(raw)) <= 600


@needs_passkey
@pytest.mark.parametrize("form", ["cookie", "token"])
async def test_registration_links_the_passkey_and_opens_the_session(
    client: AsyncClient,
    session: AsyncSession,
    sent: list[httpx.Request],
    clock: list[int],
    form: str,
) -> None:
    """The account keeps its handle, its passkey and its language.

    The passkey signs in afterwards, and no notice goes out.
    """
    authenticator = Authenticator()
    response = await register(
        client, authenticator, await new_code(client, sent, clock, email=EMAIL), form
    )
    assert response.status_code == (204 if form == "cookie" else 200)
    if form == "cookie":
        assert sessions.COOKIE in SimpleCookie(response.headers["set-cookie"])
    else:
        assert set(response.json()) == {
            "access_token",
            "token_type",
            "expires_in",
            "refresh_token",
        }
    account = (await session.scalars(sa.select(Account))).one()
    assert (account.email, account.role, account.language) == (EMAIL, Role.USER, "es")
    passkey = (await session.scalars(sa.select(Passkey))).one()
    assert passkey.credential_id == authenticator.credential_id
    assert (passkey.name, passkey.transports, passkey.uv_initialized) == (
        "Phone",
        ["internal", "hybrid"],
        True,
    )
    assert (passkey.backup_eligible, passkey.backup_state) == (False, False)
    assert passkey.created_at == passkey.changed_at
    assert await actions(session) == ["user_created", "sensitive_create", "session_created"]
    assert len(sent) == 1
    login = await client.post("/api/auth/passkey/options")
    credential = authenticator.sign(login.json()["challenge"], account.user_handle)
    assert (await client.post("/api/auth/passkey/token", json=credential)).status_code == 200


@needs_passkey
@pytest.mark.parametrize(
    ("fmt", "status"), [("none", 200), ("packed", 200), ("packed-x5c", 400), ("fido-u2f", 400)]
)
async def test_registration_takes_none_and_self_attestation(
    client: AsyncClient, sent: list[httpx.Request], clock: list[int], fmt: str, status: int
) -> None:
    """Only none and packed without x5c are accepted.

    A packed attestation with a certificate passes the library, which
    checks no chain without roots: the server refuses it by itself.
    """
    code = await new_code(client, sent, clock, email=EMAIL)
    response = await register(client, Authenticator(), code, create={"fmt": fmt})
    assert response.status_code == status


@needs_passkey
@pytest.mark.parametrize(
    ("extensions", "status"),
    [
        ({"credProtect": 1}, 200),
        ({"credProtect": 3}, 200),
        ({"credProtect": 4}, 400),
        ({"hmac-secret": True}, 400),
    ],
)
async def test_registration_takes_only_cred_protect(
    client: AsyncClient,
    sent: list[httpx.Request],
    clock: list[int],
    recorded: list[EventLog],
    extensions: dict[str, object],
    status: int,
) -> None:
    """AuthData takes only credProtect, 1 to 3; another is named."""
    code = await new_code(client, sent, clock, email=EMAIL)
    response = await register(client, Authenticator(), code, create={"extensions": extensions})
    assert response.status_code == status
    if "hmac-secret" in extensions:
        assert recorded[-1].details == {"reason": "extensions", "extensions": ["hmac-secret"]}


@needs_passkey
async def test_registration_client_must_be_clean(
    client: AsyncClient, sent: list[httpx.Request], clock: list[int]
) -> None:
    """ClientExtensionResults must be empty, and the origin our own."""
    code = await new_code(client, sent, clock, email=EMAIL)
    challenge = (await options(client, email=EMAIL))["challenge"]
    credential = Authenticator().create(challenge)
    credential["clientExtensionResults"] = {"credProps": {"rk": True}}
    sent_body = {"email": EMAIL, "code": code, "passkeyName": "Phone", "credential": credential}
    assert (await client.post("/api/auth/register/token", json=sent_body)).status_code == 400
    for create in ({"client": {"crossOrigin": True}}, {"origin": "https://evil.example"}):
        assert (await register(client, Authenticator(), code, create=create)).status_code == 400


@needs_passkey
async def test_credential_id_longer_than_1023_bytes_or_taken_fails(
    client: AsyncClient, session: AsyncSession, sent: list[httpx.Request], clock: list[int]
) -> None:
    """A credential ID of more than 1023 bytes, or another's, fails."""
    code = await new_code(client, sent, clock, email=EMAIL)
    long = Authenticator()
    long.credential_id = bytes(1024)
    assert (await register(client, long, code)).status_code == 400
    first = Authenticator()
    assert (await register(client, first, code)).status_code == 200
    await session.execute(sa.update(Account).values(email="other@example.com"))
    copy = Authenticator()
    copy.credential_id = first.credential_id
    code = await new_code(client, sent, clock, email=EMAIL)
    assert (await register(client, copy, code)).status_code == 400


@needs_passkey
async def test_wrong_code_fails_and_a_failed_passkey_keeps_the_code(
    client: AsyncClient, session: AsyncSession, sent: list[httpx.Request], clock: list[int]
) -> None:
    """A wrong code is a 400 of its type; a bad passkey spends none."""
    code = await new_code(client, sent, clock, email=EMAIL)
    wrong = f"{(int(code) + 1) % 10**6:06d}"
    response = await register(client, Authenticator(), wrong)
    assert response.status_code == 400
    assert response.json()["type"] == errors.INVALID_CODE.uri
    bad = {"origin": "https://evil.example"}
    assert (await register(client, Authenticator(), code, create=bad)).status_code == 400
    assert (await register(client, Authenticator(), code)).status_code == 200
    assert await session.scalar(sa.select(sa.func.count()).select_from(Account)) == 1


@needs_passkey
async def test_setup_code_registers_the_first_superadmin_once(
    client: AsyncClient, session: AsyncSession, sent: list[httpx.Request], clock: list[int]
) -> None:
    """The setup code makes a superadmin while there is none."""
    response = await register(client, Authenticator(), None, setupCode="wrong")
    assert response.status_code == 403
    response = await register(client, Authenticator(), None, setupCode=settings.setup_code)
    assert response.status_code == 200
    assert await session.scalar(sa.select(Account.role)) == Role.SUPERADMIN
    await session.execute(sa.update(Account).values(email="first@example.com"))
    response = await register(client, Authenticator(), None, setupCode=settings.setup_code)
    assert response.status_code == 403
    code = await new_code(client, sent, clock, email=EMAIL)
    assert (await register(client, Authenticator(), code)).status_code == 200
    roles = await session.scalars(sa.select(Account.role).order_by(Account.created_at))
    assert sorted(roles) == [Role.SUPERADMIN, Role.USER]


@needs_passkey
async def test_setup_code_replaces_the_code(
    client: AsyncClient, session: AsyncSession, sent: list[httpx.Request], clock: list[int]
) -> None:
    """The superadmin registers without a code sent to its address.

    With the code and the setup code, or with neither, it is a 422.
    """
    code = await new_code(client, sent, clock, email=EMAIL)
    both = await register(client, Authenticator(), code, setupCode=settings.setup_code)
    assert both.status_code == 422
    assert (await register(client, Authenticator(), None)).status_code == 422
    sent.clear()
    response = await register(client, Authenticator(), None, setupCode=settings.setup_code)
    assert response.status_code == 200
    assert sent == []
    assert await session.scalar(sa.select(Account.role)) == Role.SUPERADMIN


@needs_passkey
async def test_superadmin_registers_a_passkey_that_verified_the_user(
    client: AsyncClient, session: AsyncSession, sent: list[httpx.Request], clock: list[int]
) -> None:
    """With the setup code, a passkey without the UV flag fails."""
    response = await register(client, Authenticator(flags=UP), None, setupCode=settings.setup_code)
    assert response.status_code == 403
    assert response.json()["type"] == errors.USER_VERIFICATION_REQUIRED.uri
    assert await session.scalar(sa.select(sa.func.count()).select_from(Account)) == 0


@needs_passkey
async def test_registration_by_phone_verifies_the_phone(
    client: AsyncClient, session: AsyncSession, sent: list[httpx.Request], clock: list[int]
) -> None:
    """A phone registers with the code of its SMS, and only with it."""
    code = await new_code(client, sent, clock, phone=PHONE)
    challenge = (await options(client, phone=PHONE))["challenge"]
    credential = Authenticator().create(challenge)
    registration = {"phone": PHONE, "code": code, "passkeyName": "Phone", "credential": credential}
    other = {**registration, "phone": "+522221234567"}
    assert (await client.post("/api/auth/register/token", json=other)).status_code == 400
    challenge = (await options(client, phone=PHONE))["challenge"]
    registration["credential"] = Authenticator().create(challenge)
    assert (await client.post("/api/auth/register/token", json=registration)).status_code == 200
    account = (await session.scalars(sa.select(Account))).one()
    assert (account.phone, account.email) == (PHONE, None)
