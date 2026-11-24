"""The password: signing in, adding and changing it, its blocklist.

The product may not offer the password: then these tests skip.
"""

import json
import re
import unicodedata
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from http.cookies import SimpleCookie
from pathlib import Path

import httpx
import pytest
import sqlalchemy as sa
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession

from app import errors, methods
from app.config import settings
from app.dependencies import PrincipalDep
from app.enums import Method, Role
from app.methods import METHODS
from app.models.account.account import Account
from app.models.account.account_session import AccountSession
from app.models.account.password import Password
from app.models.event.event_log import EventLog
from app.services import events, limits, passwords, sessions

pytestmark = pytest.mark.skipif(
    Method.PASSWORD not in METHODS, reason="the product offers no password"
)

EMAIL = "ana@example.com"
ORIGIN = {"Origin": "https://test"}
# Where the product offers the passkey, an admin signs in only with it.
WITH_PASSKEY = frozenset({Method.PASSKEY, Method.PASSWORD})
PHONE = "+56221234567"
PASSWORD = "Correct horse battery"
NEW = "Staple of a purple ocean"
# On the list of the NCSC, with 8 characters or more.
COMMON = "password123"


@pytest.fixture
async def account(session: AsyncSession) -> Account:
    """Create an account with an email, a phone and a password."""
    row = Account(email=EMAIL, phone=PHONE, role=Role.USER, language="es")
    session.add(row)
    await session.flush()
    session.add(Password(account_id=row.id, hash=passwords.hash_password(PASSWORD)))
    await session.flush()
    return row


probe = FastAPI()
errors.install(probe)


@probe.get("/whoami")
async def whoami(principal: PrincipalDep) -> dict[str, str]:
    """Answer the account of the session that calls."""
    return {"account": str(principal.account.id)}


@pytest.fixture
async def guarded(database: AsyncConnection) -> AsyncIterator[AsyncClient]:
    """Call a route that only a signed-in account reaches."""
    async with AsyncClient(transport=ASGITransport(app=probe), base_url="http://test") as client:
        yield client


@pytest.fixture
def recorded(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Collect the events written in their own transaction."""
    found: list[str] = []

    async def record(row: EventLog) -> None:
        """Keep the action of the event."""
        found.append(row.action)

    monkeypatch.setattr(events, "record", record)
    return found


def with_cookie(token: str) -> dict[str, str]:
    """Send a session cookie: the client does not keep a Secure one."""
    return {"Cookie": f"{sessions.COOKIE}={token}"}


async def sign_in_web(client: AsyncClient) -> str:
    """Sign in the web with the password and return its cookie."""
    response = await client.post(
        "/api/auth/password/cookie", json={"email": EMAIL, "password": PASSWORD}
    )
    assert response.status_code == 204
    return SimpleCookie(response.headers["set-cookie"])[sessions.COOKIE].value


async def actions(session: AsyncSession) -> list[str]:
    """Return the actions of the events, in order."""
    return list(await session.scalars(sa.select(EventLog.action).order_by(EventLog.id)))


async def sign_in(client: AsyncClient, password: str = PASSWORD) -> Response:
    """Sign in an app with the password."""
    return await client.post(
        "/api/auth/password/token", json={"email": EMAIL, "password": password}
    )


def bearer(tokens: dict[str, str]) -> dict[str, str]:
    """Present the access token of an app."""
    return {"Authorization": f"Bearer {tokens['access_token']}"}


async def put(client: AsyncClient, tokens: dict[str, str], password: str) -> Response:
    """Add or change the password of the session's account."""
    return await client.put(
        "/api/account/password", json={"password": password}, headers=bearer(tokens)
    )


def test_blocklist_holds_the_common_passwords_of_8_or_more() -> None:
    """The list has the 3000 most common passwords of 8 or more.

    Each one is in NFC and casefold, once.
    """
    lines = (Path(passwords.__file__).parent.parent / "blocklist.txt").read_text(encoding="utf-8")
    entries = lines.splitlines()
    assert len(entries) >= 3000
    assert all(len(entry) >= 8 for entry in entries)
    assert all(entry == unicodedata.normalize("NFC", entry).casefold() for entry in entries)
    assert len(set(entries)) == len(entries)
    assert {"password", "qwertyuiop"} <= passwords.BLOCKLIST


@pytest.mark.parametrize("password", [COMMON, "PassWord123"])
async def test_password_on_the_blocklist_is_refused_with_its_type(
    client: AsyncClient, session: AsyncSession, account: Account, password: str
) -> None:
    """A password of the list, in any case, is a 422 of its type.

    The refusal stays in event_log, and the password does not change.
    """
    tokens = (await sign_in(client)).json()
    response = await put(client, tokens, password)
    assert (response.status_code, response.json()["type"]) == (422, errors.PASSWORD_BLOCKED.uri)
    action = await session.scalar(
        sa.select(EventLog.action).where(EventLog.action == "authn_password_change_fail")
    )
    assert action == "authn_password_change_fail"
    assert (await sign_in(client)).status_code == 200


@pytest.mark.parametrize(
    ("password", "status"),
    [
        ("a" * 7, 422),
        ("Kühlschrank", 204),
        ("e\u0301abcdef", 422),
        ("ü" * 128, 204),
        ("ü" * 129, 422),
    ],
)
async def test_password_has_8_to_128_code_points_in_nfc(
    client: AsyncClient, account: Account, password: str, status: int
) -> None:
    """Each code point counts as a character, after NFC."""
    tokens = (await sign_in(client)).json()
    assert (await put(client, tokens, password)).status_code == status


async def test_password_is_added_and_notifies(
    client: AsyncClient,
    session: AsyncSession,
    account: Account,
    sent: list[httpx.Request],
) -> None:
    """An account without a password adds one: a 201 and a notice."""
    await session.execute(sa.delete(Password))
    caller = sessions.Client(ip_address="127.0.0.1", user_agent="test")
    issued = await sessions.open_app(session, account, caller, "es")
    await session.flush()
    tokens = {"access_token": issued.access_token}
    assert (await put(client, tokens, NEW)).status_code == 201
    row = await session.get_one(Password, account.id)
    assert row.created_at == row.changed_at
    assert sorted(json.loads(request.content)["to"] for request in sent) == sorted([PHONE, EMAIL])
    assert all(settings.contact in request.content.decode() for request in sent)
    assert "authn_password_change" in await session.scalars(sa.select(EventLog.action))
    assert (await sign_in(client, NEW)).status_code == 200


async def test_change_closes_the_other_sessions(
    client: AsyncClient,
    guarded: AsyncClient,
    session: AsyncSession,
    account: Account,
    sent: list[httpx.Request],
) -> None:
    """Changing the password keeps this session and closes the rest."""
    other = (await sign_in(client)).json()
    tokens = (await sign_in(client)).json()
    assert (await put(client, tokens, NEW)).status_code == 204
    assert (await guarded.get("/whoami", headers=bearer(other))).status_code == 401
    assert (await guarded.get("/whoami", headers=bearer(tokens))).status_code == 200
    assert await session.scalar(sa.select(sa.func.count()).select_from(AccountSession)) == 1
    expired = await session.scalars(
        sa.select(EventLog.details).where(EventLog.action == "session_expired")
    )
    assert list(expired) == [{"reason": "password_change"}]
    assert (await sign_in(client, PASSWORD)).status_code == 401
    assert len(sent) == 2


async def test_change_resets_the_failures_and_enables(
    client: AsyncClient, session: AsyncSession, account: Account
) -> None:
    """A new password is another secret: no failures, no wait."""
    tokens = (await sign_in(client)).json()
    later = datetime.now(UTC) + timedelta(hours=1)
    await session.execute(
        sa.update(Password).values(failures=100, retry_at=later, disabled_at=datetime.now(UTC))
    )
    assert (await put(client, tokens, NEW)).status_code == 204
    row = await session.get_one(Password, account.id)
    await session.refresh(row)
    assert (row.failures, row.retry_at, row.disabled_at) == (0, None, None)


async def test_admin_does_not_add_a_password(
    client: AsyncClient, session: AsyncSession, account: Account, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An admin signs in only with a passkey: a password is a 403."""
    monkeypatch.setattr(methods, "METHODS", WITH_PASSKEY)
    tokens = (await sign_in(client)).json()
    await session.execute(sa.update(Account).values(role=Role.ADMIN))
    assert (await put(client, tokens, NEW)).status_code == 403


async def test_password_change_needs_a_reauth(
    client: AsyncClient, session: AsyncSession, account: Account
) -> None:
    """Adding or changing a password asks to authenticate again."""
    tokens = (await sign_in(client)).json()
    moment = datetime.now(UTC) - timedelta(minutes=6)
    await session.execute(sa.update(AccountSession).values(authenticated_at=moment))
    response = await put(client, tokens, NEW)
    assert response.json()["type"] == errors.REAUTHENTICATION_REQUIRED.uri


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> list[int]:
    """Move the time of the rate limits by hand, in milliseconds."""
    moment = [limits.now()]
    monkeypatch.setattr(limits, "now", lambda: moment[0])
    return moment


async def code_for(client: AsyncClient, sent: list[httpx.Request], email: str) -> str:
    """Ask for the code of a new account and read it."""
    assert (await client.post("/api/auth/register/code", json={"email": email})).status_code == 204
    found = re.search(r"\d{6}", json.loads(sent[-1].content)["text"])
    assert found is not None
    return found[0]


async def test_registration_takes_a_password(
    client: AsyncClient,
    session: AsyncSession,
    sent: list[httpx.Request],
    clock: list[int],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An account registers with its code and a password.

    One on the blocklist spends no code; with the setup code, a 403.
    """
    monkeypatch.setattr(methods, "METHODS", WITH_PASSKEY)
    email = "bea@example.com"
    code = await code_for(client, sent, email)
    body = {"email": email, "code": code, "password": COMMON}
    response = await client.post("/api/auth/register/token", json=body)
    assert response.json()["type"] == errors.PASSWORD_BLOCKED.uri
    with_setup = {**body, "password": NEW, "setupCode": settings.setup_code}
    assert (await client.post("/api/auth/register/token", json=with_setup)).status_code == 403
    response = await client.post("/api/auth/register/token", json={**body, "password": NEW})
    assert response.status_code == 200
    account = (await session.scalars(sa.select(Account))).one()
    assert account.role == Role.USER
    assert await session.get(Password, account.id) is not None
    login = {"email": email, "password": NEW}
    assert (await client.post("/api/auth/password/token", json=login)).status_code == 200


@pytest.mark.parametrize(
    "extra",
    [{}, {"password": NEW, "passkeyName": "Phone", "credential": {}}, {"passkeyName": "Phone"}],
)
async def test_registration_takes_one_authenticator(
    client: AsyncClient, extra: dict[str, object]
) -> None:
    """A registration brings a named passkey or a password, not both."""
    body = {"email": "bea@example.com", "code": "123456", **extra}
    assert (await client.post("/api/auth/register/token", json=body)).status_code == 422


async def test_app_signs_in_as_the_token_endpoint(client: AsyncClient, account: Account) -> None:
    """The app gets the tokens of RFC 6749, not to be cached."""
    response = await client.post(
        "/api/auth/password/token", json={"phone": PHONE, "password": PASSWORD}
    )
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["pragma"] == "no-cache"
    body = response.json()
    assert set(body) == {"access_token", "token_type", "expires_in", "refresh_token"}
    assert (body["token_type"], body["expires_in"]) == ("Bearer", 900)


@pytest.mark.parametrize(
    "body",
    [
        {"password": PASSWORD},
        {"email": EMAIL, "phone": PHONE, "password": PASSWORD},
        {"phone": "56912345678", "password": PASSWORD},
    ],
)
async def test_login_takes_the_email_or_the_phone(
    client: AsyncClient, account: Account, body: dict[str, str]
) -> None:
    """The login takes exactly one of the email and the phone."""
    response = await client.post("/api/auth/password/cookie", json=body)
    assert response.status_code == 422


async def test_login_lowers_the_email(client: AsyncClient, account: Account) -> None:
    """The email signs in whatever its case."""
    response = await client.post(
        "/api/auth/password/cookie", json={"email": EMAIL.upper(), "password": PASSWORD}
    )
    assert response.status_code == 204


async def test_password_is_checked_in_nfc_as_it_comes(
    client: AsyncClient, session: AsyncSession, account: Account
) -> None:
    """The NFD form signs in; another case or a cut does not."""
    word = "contraseña ñandú"
    hashed = passwords.hash_password(unicodedata.normalize("NFD", word))
    await session.execute(sa.update(Password).values(hash=hashed))
    for password, status in [
        (unicodedata.normalize("NFD", word), 204),
        (unicodedata.normalize("NFC", word), 204),
        (word.upper(), 401),
        (word[:-1], 401),
    ]:
        body = {"email": EMAIL, "password": password}
        assert (await client.post("/api/auth/password/cookie", json=body)).status_code == status


async def test_wrong_password_is_a_401_and_a_failure(
    client: AsyncClient, session: AsyncSession, account: Account
) -> None:
    """A wrong password or an unknown account: a 401 and an event."""
    for email in (EMAIL, "nobody@example.com"):
        response = await client.post(
            "/api/auth/password/token", json={"email": email, "password": "wrong"}
        )
        assert response.status_code == 401
        assert response.headers["content-type"] == errors.PROBLEM_JSON
    assert await session.scalar(sa.select(Password.failures)) == 1
    assert await actions(session) == ["authn_login_fail", "authn_login_fail"]


async def test_attempt_before_the_wait_is_a_429(
    client: AsyncClient, session: AsyncSession, account: Account, recorded: list[str]
) -> None:
    """From the fifth failure, an early attempt is a 429.

    It carries Retry-After, even with the right password, which it
    does not check.
    """
    wrong = {"email": EMAIL, "password": "wrong"}
    for _ in range(5):
        assert (await client.post("/api/auth/password/cookie", json=wrong)).status_code == 401
    right = {"email": EMAIL, "password": PASSWORD}
    response = await client.post("/api/auth/password/cookie", json=right)
    assert response.status_code == 429
    assert 29 <= int(response.headers["retry-after"]) <= 30
    assert response.json()["detail"]
    assert await session.scalar(sa.select(Password.failures)) == 5
    assert recorded == ["authn_login_fail_max"]


async def test_success_resets_the_failures(
    client: AsyncClient, session: AsyncSession, account: Account
) -> None:
    """A login after the wait passes resets the failures."""
    await session.execute(
        sa.update(Password).values(failures=7, retry_at=datetime.now(UTC) - timedelta(seconds=1))
    )
    await sign_in_web(client)
    password = (await session.execute(sa.select(Password.failures, Password.retry_at))).one()
    assert tuple(password) == (0, None)
    assert "authn_login_successafterfail" in await actions(session)


async def test_hundredth_failure_disables_the_password(
    client: AsyncClient, guarded: AsyncClient, session: AsyncSession, account: Account
) -> None:
    """At 100 failures the password is disabled: a 403 of its type.

    The right password does not pass, and the sessions stay.
    """
    token = await sign_in_web(client)
    await session.execute(
        sa.update(Password).values(failures=99, retry_at=datetime.now(UTC) - timedelta(seconds=1))
    )
    wrong = {"email": EMAIL, "password": "wrong"}
    assert (await client.post("/api/auth/password/cookie", json=wrong)).status_code == 401
    assert await session.scalar(sa.select(Password.disabled_at)) is not None
    assert "authn_login_lock" in await actions(session)
    await session.execute(sa.update(Password).values(retry_at=None))
    right = {"email": EMAIL, "password": PASSWORD}
    response = await client.post("/api/auth/password/cookie", json=right)
    assert response.status_code == 403
    assert response.json()["type"] == errors.AUTHENTICATOR_DISABLED.uri
    assert (await guarded.get("/whoami", headers=with_cookie(token))).status_code == 200


async def test_admin_does_not_sign_in_with_a_password(
    client: AsyncClient, session: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An admin's failures count; the right password is a 403."""
    monkeypatch.setattr(methods, "METHODS", WITH_PASSKEY)
    account = Account(email="ana.admin@example.com", role=Role.ADMIN, language="es")
    session.add(account)
    await session.flush()
    session.add(Password(account_id=account.id, hash=passwords.hash_password("Correct horse")))
    await session.flush()
    wrong = {"email": "ana.admin@example.com", "password": "Wrong horse"}
    assert (await client.post("/api/auth/password/token", json=wrong)).status_code == 401
    assert await session.scalar(sa.select(Password.failures)) == 1
    login = {"email": "ana.admin@example.com", "password": "Correct horse"}
    assert (await client.post("/api/auth/password/token", json=login)).status_code == 403
    assert await session.scalar(sa.select(Password.failures)) == 1
    await session.execute(sa.update(Account).values(role=Role.USER))
    assert (await client.post("/api/auth/password/token", json=login)).status_code == 200


async def test_reauth_with_the_password_renews_the_session(
    client: AsyncClient, session: AsyncSession, account: Account
) -> None:
    """The password authenticates the session again; a wrong one, no."""
    tokens = (await sign_in(client)).json()
    moment = datetime.now(UTC) - timedelta(minutes=10)
    await session.execute(sa.update(AccountSession).values(authenticated_at=moment))
    headers = bearer(tokens)
    wrong = await client.post(
        "/api/auth/reauth/password", json={"password": "wrong"}, headers=headers
    )
    assert wrong.status_code == 401
    response = await client.post(
        "/api/auth/reauth/password", json={"password": PASSWORD}, headers=headers
    )
    assert response.status_code == 200
    renewed = await session.scalar(sa.select(AccountSession.authenticated_at))
    assert renewed is not None
    assert datetime.now(UTC) - renewed < timedelta(minutes=1)


async def test_admin_without_passkey_uses_the_password(
    client: AsyncClient,
    session: AsyncSession,
    sent: list[httpx.Request],
    clock: list[int],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Where the product offers no passkey, the admin has a password.

    The setup code registers it, and it signs in and changes it.
    """
    monkeypatch.setattr(methods, "METHODS", frozenset({Method.PASSWORD}))
    email = "admin@example.com"
    code = await code_for(client, sent, email)
    body = {"email": email, "code": code, "password": NEW, "setupCode": settings.setup_code}
    assert (await client.post("/api/auth/register/token", json=body)).status_code == 200
    assert await session.scalar(sa.select(Account.role)) == Role.ADMIN
    login = {"email": email, "password": NEW}
    response = await client.post("/api/auth/password/token", json=login)
    assert response.status_code == 200
    assert (await put(client, response.json(), PASSWORD)).status_code == 204
