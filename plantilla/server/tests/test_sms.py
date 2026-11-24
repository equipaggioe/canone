"""The code of an SMS: signing in, authenticating again, registering.

The product may not offer the SMS code: then these tests skip.
"""

import json
import re
from datetime import UTC, datetime, timedelta
from http.cookies import SimpleCookie

import httpx
import pytest
import sqlalchemy as sa
from httpx import AsyncClient, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app import errors, methods
from app.config import settings
from app.enums import Method, Role
from app.methods import METHODS
from app.models.account.account import Account
from app.models.account.account_session import AccountSession
from app.models.account.phone import Phone
from app.models.event.event_log import EventLog
from app.services import account as account_service
from app.services import codes, limits, sessions, sms
from app.services.sessions import Client

pytestmark = pytest.mark.skipif(Method.SMS not in METHODS, reason="the product offers no SMS code")

PHONE = "+56221234567"
NEW_PHONE = "+56221234568"
HOST = f"app.{settings.domain}"
WITH_PASSKEY = frozenset({Method.PASSKEY, Method.SMS})


async def holder(session: AsyncSession, role: Role = Role.USER) -> Account:
    """Create an account with a phone, its authenticator."""
    row = Account(phone=PHONE, role=role, language="es")
    session.add(row)
    await session.flush()
    sms.bind(session, row)
    await session.flush()
    return row


@pytest.fixture
async def account(session: AsyncSession) -> Account:
    """Create an account that signs in with the code of its phone."""
    return await holder(session)


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> list[int]:
    """Move the time of the rate limits by hand, in milliseconds."""
    moment = [limits.now()]
    monkeypatch.setattr(limits, "now", lambda: moment[0])
    return moment


def code_in(request: httpx.Request) -> str:
    """Read the code of an SMS sent to Equipaggio."""
    found = re.search(r"\d{6}", json.loads(request.content)["body"])
    assert found is not None
    return found[0]


async def ask(client: AsyncClient, phone: str = PHONE) -> Response:
    """Ask for the code to sign in, from a surface of the domain."""
    return await client.post("/api/auth/sms/code", json={"phone": phone}, headers={"Host": HOST})


async def sign_in(client: AsyncClient, code: str, form: str = "token") -> Response:
    """Sign in with the phone and a code."""
    return await client.post(f"/api/auth/sms/{form}", json={"phone": PHONE, "code": code})


def other(code: str) -> str:
    """Return a code that is not this one."""
    return f"{(int(code) + 1) % 10**6:06d}"


async def actions(session: AsyncSession) -> list[str]:
    """Return the actions of the events, in order."""
    return list(await session.scalars(sa.select(EventLog.action).order_by(EventLog.id)))


@pytest.mark.usefixtures("account")
@pytest.mark.parametrize("form", ["cookie", "token"])
async def test_sms_signs_in_the_web_and_the_app(
    client: AsyncClient, session: AsyncSession, sent: list[httpx.Request], form: str
) -> None:
    """The code of the SMS opens the session by its two routes.

    An app receives what the token endpoint answers.
    """
    assert (await ask(client)).status_code == 204
    assert json.loads(sent[-1].content)["to"] == PHONE
    response = await sign_in(client, code_in(sent[-1]), form)
    if form == "cookie":
        assert response.status_code == 204
        assert sessions.COOKIE in SimpleCookie(response.headers["set-cookie"])
    else:
        assert response.status_code == 200
        assert set(response.json()) == {
            "access_token",
            "token_type",
            "expires_in",
            "refresh_token",
        }
        assert response.headers["cache-control"] == "no-store"
        assert response.headers["pragma"] == "no-cache"
    assert await actions(session) == ["authn_login_success", "session_created"]


async def test_code_to_an_unknown_phone_is_a_404(
    client: AsyncClient, account: Account, sent: list[httpx.Request]
) -> None:
    """The tenth 404 to an IP in 15 minutes blocks it 30 minutes."""
    for _ in range(10):
        assert (await ask(client, NEW_PHONE)).status_code == 404
    response = await ask(client)
    assert response.status_code == 429
    assert 1790 <= int(response.headers["retry-after"]) <= 1800
    assert sent == []


@pytest.mark.usefixtures("account")
async def test_wrong_code_is_invalid_code_and_a_failure_of_the_phone(
    client: AsyncClient, session: AsyncSession, sent: list[httpx.Request], clock: list[int]
) -> None:
    """A wrong code is a 400 of its type, and a failure of the phone.

    A new code does not reset it; a sign-in does.
    """
    assert (await ask(client)).status_code == 204
    response = await sign_in(client, other(code_in(sent[-1])))
    assert response.status_code == 400
    assert response.json()["type"] == errors.INVALID_CODE.uri
    assert await session.scalar(sa.select(Phone.failures)) == 1
    assert await actions(session) == ["authn_login_fail"]
    clock[0] += 61_000
    assert (await ask(client)).status_code == 204
    assert await session.scalar(sa.select(Phone.failures)) == 1
    assert (await sign_in(client, code_in(sent[-1]))).status_code == 200
    assert await session.scalar(sa.select(Phone.failures)) == 0


async def test_phone_waits_and_disables_like_any_authenticator(
    client: AsyncClient, session: AsyncSession, account: Account, sent: list[httpx.Request]
) -> None:
    """From the fifth failure it waits, and at the hundredth disables.

    Neither one gets an SMS, and a disabled phone takes no right code.
    """
    await session.execute(sa.update(Phone).values(failures=4))
    wrong = other(await codes.issue(sms.PURPOSE, PHONE))
    assert (await sign_in(client, wrong)).status_code == 400
    response = await ask(client)
    assert response.status_code == 429
    assert 1 <= int(response.headers["retry-after"]) <= 30
    assert (await sign_in(client, wrong)).status_code == 429
    late = datetime.now(UTC) - timedelta(seconds=1)
    await session.execute(sa.update(Phone).values(failures=99, retry_at=late))
    assert (await sign_in(client, wrong)).status_code == 400
    assert await session.scalar(sa.select(Phone.disabled_at)) is not None
    assert "authn_login_lock" in await actions(session)
    await session.execute(sa.update(Phone).values(retry_at=None))
    response = await ask(client)
    assert response.status_code == 403
    assert response.json()["type"] == errors.AUTHENTICATOR_DISABLED.uri
    right = await codes.issue(sms.PURPOSE, PHONE)
    assert (await sign_in(client, right)).status_code == 403
    assert sent == []


async def test_superadmin_does_not_sign_in_with_sms(
    client: AsyncClient,
    session: AsyncSession,
    sent: list[httpx.Request],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """With the passkey in the product, no code goes to a superadmin.

    Asking one is a 403, a wrong code counts as anyone's, and a right
    one is a 403 too.
    """
    monkeypatch.setattr(methods, "METHODS", WITH_PASSKEY)
    await holder(session, Role.SUPERADMIN)
    assert (await ask(client)).status_code == 403
    assert sent == []
    code = await codes.issue(sms.PURPOSE, PHONE)
    response = await sign_in(client, other(code))
    assert response.status_code == 400
    assert response.json()["type"] == errors.INVALID_CODE.uri
    assert await session.scalar(sa.select(Phone.failures)) == 1
    assert (await sign_in(client, code)).status_code == 403
    monkeypatch.setattr(methods, "METHODS", frozenset({Method.SMS}))
    assert (await ask(client)).status_code == 204
    assert (await sign_in(client, code_in(sent[-1]))).status_code == 200


async def test_reauth_with_sms_renews_the_session(
    client: AsyncClient, session: AsyncSession, account: Account, sent: list[httpx.Request]
) -> None:
    """The code to the phone of the account authenticates it again.

    The session renews with new tokens; an account without a phone is a
    409.
    """
    issued = await sessions.open_app(session, account, Client("127.0.0.1", "test"), "es")
    moment = datetime.now(UTC) - timedelta(minutes=10)
    await session.execute(sa.update(AccountSession).values(authenticated_at=moment))
    bearer = {"Authorization": f"Bearer {issued.access_token}"}
    response = await client.post("/api/auth/reauth/sms/code", headers={**bearer, "Host": HOST})
    assert response.status_code == 204
    assert json.loads(sent[-1].content)["to"] == PHONE
    wrong = {"code": other(code_in(sent[-1]))}
    assert (
        await client.post("/api/auth/reauth/sms", json=wrong, headers=bearer)
    ).status_code == 400
    right = {"code": code_in(sent[-1])}
    response = await client.post("/api/auth/reauth/sms", json=right, headers=bearer)
    assert response.status_code == 200
    assert response.json()["access_token"] != issued.access_token
    renewed = await session.scalar(sa.select(AccountSession.authenticated_at))
    assert renewed is not None
    assert datetime.now(UTC) - renewed < timedelta(minutes=1)
    fresh = {"Authorization": f"Bearer {response.json()['access_token']}"}
    await session.execute(sa.update(Account).values(phone=None, email="ana@example.com"))
    response = await client.post("/api/auth/reauth/sms/code", headers={**fresh, "Host": HOST})
    assert response.status_code == 409


async def test_registration_by_phone_takes_no_authenticator(
    client: AsyncClient,
    session: AsyncSession,
    sent: list[httpx.Request],
    clock: list[int],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A phone registers with its code alone, and signs in with SMS.

    An email needs an authenticator, and so does a product without the
    SMS code.
    """
    headers = {"Host": HOST}
    code = {"phone": PHONE}
    assert (
        await client.post("/api/auth/register/code", json=code, headers=headers)
    ).status_code == 204
    registration = {"phone": PHONE, "code": code_in(sent[-1])}
    monkeypatch.setattr(methods, "METHODS", frozenset({Method.PASSKEY}))
    response = await client.post("/api/auth/register/token", json=registration)
    assert response.status_code == 422
    assert response.json()["errors"] == [{"detail": "send a passkey or a password", "pointer": ""}]
    email = {"email": "ana@example.com", "code": "123456"}
    monkeypatch.setattr(methods, "METHODS", METHODS)
    response = await client.post("/api/auth/register/token", json=email)
    assert response.json()["errors"] == [{"detail": "send a passkey or a password", "pointer": ""}]
    assert (await client.post("/api/auth/register/token", json=registration)).status_code == 200
    account = (await session.scalars(sa.select(Account))).one()
    assert await session.get(Phone, account.id) is not None
    clock[0] += 61_000
    assert (await ask(client)).status_code == 204
    assert (await sign_in(client, code_in(sent[-1]))).status_code == 200


async def test_new_phone_resets_its_failures(session: AsyncSession, account: Account) -> None:
    """Another number is another authenticator: it starts enabled."""
    before = datetime.now(UTC) - timedelta(days=1)
    await session.execute(
        sa.update(Phone).values(failures=100, disabled_at=before, changed_at=before)
    )
    code = await codes.issue(account_service.PURPOSE, f"{account.id}:{NEW_PHONE}")
    client = Client("127.0.0.1", "test")
    await account_service.change_phone(session, account, NEW_PHONE, code, client)
    await session.flush()
    row = await session.get(Phone, account.id, populate_existing=True)
    assert row is not None
    assert (row.failures, row.retry_at, row.disabled_at) == (0, None, None)
    assert row.changed_at > before


async def check_now(session: AsyncSession, change: sa.Executable | Account) -> None:
    """Write a change in a savepoint, and run the deferred checks."""
    async with session.begin_nested():
        if isinstance(change, Account):
            session.add(change)
            await session.flush()
        else:
            await session.execute(change)
        await session.execute(sa.text("SET CONSTRAINTS ALL IMMEDIATE"))


async def test_the_database_refuses_a_phone_without_its_row(session: AsyncSession) -> None:
    """A number without its row in phone fails when the constraints run.

    The trigger is deferred to the commit: the registration writes the
    account first and then its phone.
    """
    unbound = Account(phone=PHONE, role=Role.USER, language="es")
    with pytest.raises(IntegrityError):
        await check_now(session, unbound)
    await session.execute(sa.text("SET CONSTRAINTS ALL DEFERRED"))
    await holder(session)
    await session.execute(sa.text("SET CONSTRAINTS ALL IMMEDIATE"))
    with pytest.raises(IntegrityError):
        await check_now(session, sa.delete(Phone))
