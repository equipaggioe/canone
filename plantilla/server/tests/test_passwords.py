"""Adding and changing a password, and its blocklist."""

import json
import re
import unicodedata
from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx
import pytest
import sqlalchemy as sa
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app import errors
from app.config import settings
from app.enums import Role
from app.models.account.account import Account
from app.models.account.account_session import AccountSession
from app.models.account.password import Password
from app.models.event.event_log import EventLog
from app.services import limits, passwords
from tests.authenticator import Authenticator, register

EMAIL = "ana@example.com"
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
    authenticator = Authenticator()
    await register(session, account, authenticator)
    options = await client.post("/api/auth/passkey/options")
    credential = authenticator.sign(options.json()["challenge"], account.user_handle)
    tokens = (await client.post("/api/auth/passkey/token", json=credential)).json()
    assert (await put(client, tokens, NEW)).status_code == 201
    row = await session.get_one(Password, account.id)
    assert row.created_at == row.changed_at
    assert sorted(json.loads(request.content)["to"] for request in sent) == sorted([PHONE, EMAIL])
    assert all(settings.contact in request.content.decode() for request in sent)
    assert "authn_password_change" in await session.scalars(sa.select(EventLog.action))
    assert (await sign_in(client, NEW)).status_code == 200


async def test_change_closes_the_other_sessions(
    client: AsyncClient, session: AsyncSession, account: Account, sent: list[httpx.Request]
) -> None:
    """Changing the password keeps this session and closes the rest."""
    other = (await sign_in(client)).json()
    tokens = (await sign_in(client)).json()
    assert (await put(client, tokens, NEW)).status_code == 204
    passkeys = "/api/account/passkeys"
    assert (await client.get(passkeys, headers=bearer(other))).status_code == 401
    assert (await client.get(passkeys, headers=bearer(tokens))).status_code == 200
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
    client: AsyncClient, session: AsyncSession, account: Account
) -> None:
    """An admin signs in only with a passkey: a password is a 403."""
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
    client: AsyncClient, session: AsyncSession, sent: list[httpx.Request], clock: list[int]
) -> None:
    """An account registers with its code and a password.

    One on the blocklist spends no code; with the setup code, a 403.
    """
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
