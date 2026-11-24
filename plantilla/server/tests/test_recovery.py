"""Recovering an account: the code sent, the saved code and the wait.

The product may offer neither the passkey nor the password: then these
tests skip.
"""

import json
import re
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
import pytest
import sqlalchemy as sa
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession
from webauthn.helpers import base64url_to_bytes

from app import errors
from app.config import settings
from app.enums import Address, Method, Role
from app.methods import METHODS
from app.models.account.account import Account
from app.models.account.account_session import AccountSession
from app.models.account.passkey import Passkey
from app.models.account.password import Password
from app.models.account.recovery import Recovery
from app.models.account.recovery_address import RecoveryAddress
from app.models.account.recovery_code import RecoveryCode
from app.services import limits, passwords, recovery, sessions
from app.services.sessions import Client
from tests.authenticator import Authenticator, register

pytestmark = pytest.mark.skipif(
    not METHODS >= {Method.PASSKEY, Method.PASSWORD},
    reason="the product offers not both the passkey and the password",
)

EMAIL = "ana@example.com"
PHONE = "+56221234567"
PASSWORD = "Correct horse battery"
NEW = "Staple of a purple ocean"
HOST = f"app.{settings.domain}"
CLIENT = Client("127.0.0.1", "test")


async def holder(session: AsyncSession, role: Role = Role.USER) -> Account:
    """Create an account with an email, a phone and a password."""
    row = Account(email=EMAIL, phone=PHONE, role=role, language="es")
    session.add(row)
    await session.flush()
    session.add(Password(account_id=row.id, hash=passwords.hash_password(PASSWORD)))
    await session.flush()
    return row


@pytest.fixture
async def account(session: AsyncSession) -> Account:
    """Create an account without a passkey."""
    return await holder(session)


@pytest.fixture
async def passkey(session: AsyncSession, account: Account) -> Authenticator:
    """Give the account a passkey."""
    authenticator = Authenticator()
    await register(session, account, authenticator)
    return authenticator


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> list[int]:
    """Move the time of the rate limits by hand, in milliseconds."""
    moment = [limits.now()]
    monkeypatch.setattr(limits, "now", lambda: moment[0])
    return moment


def sent_body(request: httpx.Request) -> dict[str, Any]:
    """Read the JSON a request sent to Equipaggio."""
    found: dict[str, Any] = json.loads(request.content)
    return found


def code_in(request: httpx.Request) -> str:
    """Read the code of an email or an SMS sent to Equipaggio."""
    sent = sent_body(request)
    found = re.search(r"\d{6}", sent.get("text") or sent["body"])
    assert found is not None
    return found[0]


def other(code: str) -> str:
    """Return a code that is not this one."""
    return f"{(int(code) + 1) % 10**6:06d}"


async def ask(client: AsyncClient, clock: list[int], **identifier: str) -> Response:
    """Ask for the code to recover, a minute after the previous one."""
    clock[0] += 61_000
    return await client.post("/api/auth/recovery/code", json=identifier, headers={"Host": HOST})


async def new_code(
    client: AsyncClient, sent: list[httpx.Request], clock: list[int], **identifier: str
) -> str:
    """Ask for a code and read it from Equipaggio."""
    assert (await ask(client, clock, **identifier)).status_code == 204
    return code_in(sent[-1])


async def recover(client: AsyncClient, code: str, **extra: str) -> Response:
    """Reset the password of the account by its email."""
    body = {"email": EMAIL, "code": code, "password": NEW, **extra}
    return await client.post("/api/auth/recovery/password", json=body)


async def signs_in(client: AsyncClient, password: str) -> bool:
    """Tell whether the password signs in."""
    login = {"email": EMAIL, "password": password}
    return (await client.post("/api/auth/password/token", json=login)).status_code == 200


def to(sent: list[httpx.Request]) -> set[str]:
    """Return who the messages went to."""
    return {sent_body(request)["to"] for request in sent}


@pytest.mark.usefixtures("account")
async def test_recovery_code_goes_to_the_email_or_the_phone(
    client: AsyncClient, sent: list[httpx.Request], clock: list[int]
) -> None:
    """The holder chooses the email or the phone of the account."""
    await new_code(client, sent, clock, email=EMAIL)
    assert sent_body(sent[-1])["to"] == EMAIL
    await new_code(client, sent, clock, phone=PHONE)
    assert sent_body(sent[-1])["to"] == PHONE
    assert sent_body(sent[-1])["body"].split("\n")[-1].startswith(f"@{HOST} #")


@pytest.mark.usefixtures("account")
@pytest.mark.skipif(Method.SMS not in METHODS, reason="the product offers no SMS code")
async def test_unknown_address_is_a_404_counted_with_the_sms_code(
    client: AsyncClient, clock: list[int]
) -> None:
    """The 404 of both codes block the IP together on the tenth."""
    for _ in range(5):
        assert (await ask(client, clock, email="nobody@example.com")).status_code == 404
    for _ in range(5):
        sms = await client.post(
            "/api/auth/sms/code", json={"phone": "+56221234568"}, headers={"Host": HOST}
        )
        assert sms.status_code == 404
    assert (await ask(client, clock, email=EMAIL)).status_code == 429


async def test_password_recovery_resets_it_and_keeps_the_sessions(
    client: AsyncClient,
    session: AsyncSession,
    account: Account,
    sent: list[httpx.Request],
    clock: list[int],
) -> None:
    """Without a passkey the email code applies at once, and opens none.

    The password starts enabled, every address hears of it, and the
    code goes with its use.
    """
    issued = await sessions.open_app(session, account, CLIENT, "es")
    await session.execute(sa.update(Password).values(failures=100, disabled_at=datetime.now(UTC)))
    code = await new_code(client, sent, clock, email=EMAIL)
    response = await recover(client, code)
    assert response.status_code == 204
    assert "set-cookie" not in response.headers
    assert await signs_in(client, NEW)
    assert not await signs_in(client, PASSWORD)
    sessions_left = await session.scalar(sa.select(sa.func.count()).select_from(AccountSession))
    assert sessions_left == 2
    assert await session.get(AccountSession, issued.session_id) is not None
    assert to(sent[-2:]) == {EMAIL, PHONE}
    assert (await recover(client, code)).status_code == 400


async def test_wrong_code_counts_against_its_address(
    client: AsyncClient,
    session: AsyncSession,
    account: Account,
    sent: list[httpx.Request],
    clock: list[int],
) -> None:
    """Each address counts its failures; at 100 it stops recovering.

    The other address still recovers, and a sign-in enables both again.
    """
    code = await new_code(client, sent, clock, email=EMAIL)
    response = await recover(client, other(code))
    assert response.status_code == 400
    assert response.json()["type"] == errors.INVALID_CODE.uri
    failures = sa.select(RecoveryAddress.failures).where(RecoveryAddress.address == Address.EMAIL)
    assert await session.scalar(failures) == 1
    await session.execute(sa.update(RecoveryAddress).values(failures=99, retry_at=None))
    assert (await recover(client, other(code))).status_code == 400
    response = await ask(client, clock, email=EMAIL)
    assert response.status_code == 403
    assert response.json()["type"] == errors.RECOVERY_DISABLED.uri
    assert (await recover(client, code)).status_code == 403
    assert (await ask(client, clock, phone=PHONE)).status_code == 204
    assert await signs_in(client, PASSWORD)
    assert (await ask(client, clock, email=EMAIL)).status_code == 204
    assert await session.scalar(failures) == 0


@pytest.mark.usefixtures("passkey")
async def test_passkey_account_waits_24_hours_with_the_email_code(
    client: AsyncClient,
    session: AsyncSession,
    account: Account,
    sent: list[httpx.Request],
    clock: list[int],
) -> None:
    """The email code alone is a 202: the task applies it a day later.

    The holder sees it waiting, and every address hears both times.
    """
    response = await recover(client, await new_code(client, sent, clock, email=EMAIL))
    assert response.status_code == 202
    assert to(sent[-2:]) == {EMAIL, PHONE}
    assert await signs_in(client, PASSWORD)
    issued = await sessions.open_app(session, account, CLIENT, "es")
    bearer = {"Authorization": f"Bearer {issued.access_token}"}
    await recover_again(client, session, sent, clock)
    waiting = await client.get("/api/account/recovery", headers=bearer)
    assert waiting.status_code == 200
    assert waiting.json()["address"] == "email"
    left = datetime.fromisoformat(waiting.json()["appliesAt"]) - datetime.now(UTC)
    assert timedelta(hours=23, minutes=59) < left <= timedelta(hours=24)
    await recovery.apply_due()
    assert await session.get(Recovery, account.id) is not None
    await session.execute(sa.update(Recovery).values(applies_at=datetime.now(UTC)))
    await recovery.apply_due()
    assert await session.scalar(sa.select(Recovery)) is None
    assert await signs_in(client, NEW)
    assert to(sent[-2:]) == {EMAIL, PHONE}


async def recover_again(
    client: AsyncClient, session: AsyncSession, sent: list[httpx.Request], clock: list[int]
) -> None:
    """Ask a recovery again after a sign-in cancelled the first one."""
    assert await session.scalar(sa.select(Recovery)) is None
    response = await recover(client, await new_code(client, sent, clock, email=EMAIL))
    assert response.status_code == 202


@pytest.mark.usefixtures("passkey")
async def test_phone_code_or_saved_code_applies_at_once(
    client: AsyncClient,
    session: AsyncSession,
    account: Account,
    sent: list[httpx.Request],
    clock: list[int],
) -> None:
    """The phone, or the email with the saved code, does not wait.

    The saved code goes with its use, and a new one comes back.
    """
    phone = await new_code(client, sent, clock, phone=PHONE)
    body = {"phone": PHONE, "code": phone, "password": NEW}
    assert (await client.post("/api/auth/recovery/password", json=body)).status_code == 204
    saved, _ = await recovery.create_saved(session, account, CLIENT)
    await session.flush()
    code = await new_code(client, sent, clock, email=EMAIL)
    response = await recover(client, code, recoveryCode=saved.lower())
    assert response.status_code == 200
    replaced = response.json()["recoveryCode"]
    assert re.fullmatch(r"[A-Z2-7]{16}", replaced)
    assert await session.scalar(sa.select(Recovery)) is None
    code = await new_code(client, sent, clock, email=EMAIL)
    assert (await recover(client, code, recoveryCode=saved)).status_code == 400
    assert (await recover(client, code, recoveryCode=replaced)).status_code == 200


@pytest.mark.usefixtures("passkey")
async def test_holder_or_a_sign_in_cancels_what_waits(
    client: AsyncClient,
    session: AsyncSession,
    account: Account,
    sent: list[httpx.Request],
    clock: list[int],
) -> None:
    """The holder deletes the waiting recovery, and a sign-in too."""
    issued = await sessions.open_app(session, account, CLIENT, "es")
    bearer = {"Authorization": f"Bearer {issued.access_token}"}
    assert (await client.get("/api/account/recovery", headers=bearer)).status_code == 404
    await recover(client, await new_code(client, sent, clock, email=EMAIL))
    assert (await client.delete("/api/account/recovery", headers=bearer)).status_code == 204
    assert (await client.delete("/api/account/recovery", headers=bearer)).status_code == 404
    await recover(client, await new_code(client, sent, clock, email=EMAIL))
    assert await session.get(Recovery, account.id) is not None
    assert await signs_in(client, PASSWORD)
    assert await session.get(Recovery, account.id, populate_existing=True) is None


async def link_options(client: AsyncClient, code: str) -> Response:
    """Ask the options of the passkey of a recovery by the phone."""
    body = {"phone": PHONE, "code": code}
    return await client.post("/api/auth/recovery/options", json=body)


async def test_recovery_links_a_passkey(
    client: AsyncClient,
    session: AsyncSession,
    account: Account,
    passkey: Authenticator,
    sent: list[httpx.Request],
    clock: list[int],
) -> None:
    """The code opens the options, with the passkeys of the account.

    A wrong code opens nothing, a failed ceremony keeps the code, and
    the new passkey signs in.
    """
    code = await new_code(client, sent, clock, phone=PHONE)
    assert (await link_options(client, other(code))).status_code == 400
    found = (await link_options(client, code)).json()
    assert base64url_to_bytes(found["user"]["id"]) == account.user_handle
    excluded = [base64url_to_bytes(item["id"]) for item in found["excludeCredentials"]]
    assert excluded == [passkey.credential_id]
    new = Authenticator()
    body = {"phone": PHONE, "code": code, "passkeyName": "Laptop"}
    bad = {**body, "credential": new.create(found["challenge"], origin="https://evil.example")}
    assert (await client.post("/api/auth/recovery/passkey", json=bad)).status_code == 400
    challenge = (await link_options(client, code)).json()["challenge"]
    good = {**body, "credential": new.create(challenge)}
    assert (await client.post("/api/auth/recovery/passkey", json=good)).status_code == 204
    names = await session.scalars(sa.select(Passkey.name).order_by(Passkey.created_at))
    assert list(names) == ["Phone", "Laptop"]
    login = await client.post("/api/auth/passkey/options")
    credential = new.sign(login.json()["challenge"], account.user_handle)
    assert (await client.post("/api/auth/passkey/token", json=credential)).status_code == 200


async def test_superadmin_does_not_recover_with_a_code(
    client: AsyncClient, session: AsyncSession, sent: list[httpx.Request], clock: list[int]
) -> None:
    """Asking or presenting a code is a 403 to a superadmin."""
    await holder(session, Role.SUPERADMIN)
    assert (await ask(client, clock, email=EMAIL)).status_code == 403
    assert sent == []
    assert (await recover(client, "123456")).status_code == 403


async def test_saved_code_is_80_bits_shown_once_and_notifies(
    client: AsyncClient,
    session: AsyncSession,
    account: Account,
    sent: list[httpx.Request],
) -> None:
    """It asks a fresh authentication, and replaces the previous one.

    The server keeps only its Argon2id hash, and every address hears.
    """
    issued = await sessions.open_app(session, account, CLIENT, "es")
    bearer = {"Authorization": f"Bearer {issued.access_token}"}
    first = await client.put("/api/account/recovery-code", headers=bearer)
    assert first.status_code == 201
    saved = first.json()["recoveryCode"]
    assert re.fullmatch(r"[A-Z2-7]{16}", saved)
    stored = await session.scalar(sa.select(RecoveryCode.hash))
    assert stored is not None
    assert stored.startswith("$argon2id$")
    assert passwords.hasher.verify(saved, stored)
    assert to(sent) == {EMAIL, PHONE}
    second = await client.put("/api/account/recovery-code", headers=bearer)
    assert second.status_code == 200
    stored = await session.scalar(sa.select(RecoveryCode.hash))
    assert stored is not None
    assert not passwords.hasher.verify(saved, stored)
    moment = datetime.now(UTC) - timedelta(minutes=10)
    await session.execute(sa.update(AccountSession).values(authenticated_at=moment))
    late = await client.put("/api/account/recovery-code", headers=bearer)
    assert late.json()["type"] == errors.REAUTHENTICATION_REQUIRED.uri


@pytest.mark.usefixtures("passkey")
async def test_saved_code_counts_its_failures_and_keeps_the_sent_one(
    client: AsyncClient,
    session: AsyncSession,
    account: Account,
    sent: list[httpx.Request],
    clock: list[int],
) -> None:
    """A wrong saved code is a failure of its own; the code stays."""
    saved, _ = await recovery.create_saved(session, account, CLIENT)
    await session.flush()
    code = await new_code(client, sent, clock, email=EMAIL)
    wrong = "A" * 16 if saved != "A" * 16 else "B" * 16
    assert (await recover(client, code, recoveryCode=wrong)).status_code == 400
    assert await session.scalar(sa.select(RecoveryCode.failures)) == 1
    await session.execute(
        sa.update(RecoveryCode).values(failures=100, disabled_at=datetime.now(UTC))
    )
    response = await recover(client, code, recoveryCode=saved)
    assert response.json()["type"] == errors.RECOVERY_DISABLED.uri
    await session.execute(sa.update(RecoveryCode).values(failures=0, disabled_at=None))
    assert (await recover(client, code, recoveryCode=saved)).status_code == 200


@pytest.mark.usefixtures("account")
async def test_blocked_password_keeps_the_code(
    client: AsyncClient, sent: list[httpx.Request], clock: list[int]
) -> None:
    """A password of the blocklist is a 422; the code still serves."""
    code = await new_code(client, sent, clock, email=EMAIL)
    response = await recover(client, code, password="password123")
    assert response.status_code == 422
    assert response.json()["type"] == errors.PASSWORD_BLOCKED.uri
    assert (await recover(client, code)).status_code == 204
