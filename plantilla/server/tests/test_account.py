"""The account of the session, and the notices of its changes.

Authenticating again, its passkeys, its email and its phone, its
failures, its sessions, and deleting it.
"""

import json
import re
from datetime import UTC, datetime, timedelta
from http.cookies import SimpleCookie
from typing import Any
from uuid import UUID, uuid4

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
from app.models.account.phone import Phone
from app.models.account.recovery_address import RecoveryAddress
from app.models.event.event_log import EventLog
from app.services import limits, passwords, sessions
from app.services.sessions import Client
from tests.authenticator import Authenticator, register

EMAIL = "ana@example.com"
PHONE = "+56221234567"
PASSWORD = "Correct horse battery"
HOST = f"app.{settings.domain}"
# A test of the passkey needs the method.
needs_passkey = pytest.mark.skipif(
    Method.PASSKEY not in METHODS, reason="the product offers no passkey"
)


@pytest.fixture
async def account(session: AsyncSession) -> Account:
    """Create an account with an email, a phone and a password."""
    row = Account(email=EMAIL, phone=PHONE, role=Role.USER, language="es")
    session.add(row)
    await session.flush()
    session.add(Password(account_id=row.id, hash=passwords.hash_password(PASSWORD)))
    await session.flush()
    return row


@pytest.fixture
async def passkey(session: AsyncSession, account: Account) -> Authenticator:
    """Register an authenticator in the account."""
    authenticator = Authenticator()
    await register(session, account, authenticator)
    return authenticator


@pytest.fixture
async def app_tokens(session: AsyncSession, account: Account) -> dict[str, str]:
    """Open an app session as a login would, and return its tokens.

    The session opens without a method: a product chooses its own.
    """
    client = Client(ip_address="127.0.0.1", user_agent="test")
    issued = await sessions.open_app(session, account, client, "es")
    await session.flush()
    return {"access_token": issued.access_token, "refresh_token": issued.refresh_token}


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> list[int]:
    """Move the time of the rate limits by hand, in milliseconds."""
    moment = [limits.now()]
    monkeypatch.setattr(limits, "now", lambda: moment[0])
    return moment


def bearer(tokens: dict[str, str]) -> dict[str, str]:
    """Present the access token of an app."""
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def body(request: httpx.Request) -> dict[str, Any]:
    """Read the JSON a request sent to Equipaggio."""
    found: dict[str, Any] = json.loads(request.content)
    return found


def recipients(sent: list[httpx.Request]) -> list[str]:
    """Return who each message went to, in order."""
    return [body(request)["to"] for request in sent]


async def age(session: AsyncSession, span: timedelta) -> None:
    """Move the last authentication of every session to the past."""
    moment = datetime.now(UTC) - span
    await session.execute(sa.update(AccountSession).values(authenticated_at=moment))


async def reauth(
    client: AsyncClient, tokens: dict[str, str], authenticator: Authenticator, account: Account
) -> Response:
    """Authenticate an app again with a passkey."""
    options = await client.post("/api/auth/reauth/options", headers=bearer(tokens))
    credential = authenticator.sign(options.json()["challenge"], account.user_handle)
    return await client.post("/api/auth/reauth/passkey", json=credential, headers=bearer(tokens))


async def link(
    client: AsyncClient,
    tokens: dict[str, str],
    authenticator: Authenticator,
    passkey_id: UUID,
    name: str = "Laptop",
) -> Response:
    """Ask for the options of a new passkey and link it."""
    options = await client.post("/api/account/passkeys/options", headers=bearer(tokens))
    credential = authenticator.create(options.json()["challenge"])
    return await client.put(
        f"/api/account/passkeys/{passkey_id}",
        json={"name": name, "credential": credential},
        headers=bearer(tokens),
    )


@needs_passkey
async def test_reauth_options_list_the_passkeys_with_transports(
    client: AsyncClient, passkey: Authenticator, app_tokens: dict[str, str]
) -> None:
    """Authenticating again allows the passkeys of the account."""
    response = await client.post("/api/auth/reauth/options", headers=bearer(app_tokens))
    allowed = response.json()["allowCredentials"]
    assert allowed == [
        {
            "type": "public-key",
            "id": passkey.sign(response.json()["challenge"], None)["id"],
            "transports": ["internal"],
        }
    ]


@needs_passkey
async def test_reauth_renews_the_app_session_and_its_tokens(
    client: AsyncClient,
    session: AsyncSession,
    account: Account,
    passkey: Authenticator,
    app_tokens: dict[str, str],
) -> None:
    """The same row gets new tokens and its authentication time.

    The tokens it had stop working.
    """
    await age(session, timedelta(minutes=10))
    row = (await session.scalars(sa.select(AccountSession))).one()
    response = await reauth(client, app_tokens, passkey, account)
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    renewed = response.json()
    assert set(renewed) == {"access_token", "token_type", "expires_in", "refresh_token"}
    await session.refresh(row)
    assert datetime.now(UTC) - row.authenticated_at < timedelta(minutes=1)
    assert (await session.scalars(sa.select(AccountSession.id))).one() == row.id
    old = await client.get("/api/account/passkeys", headers=bearer(app_tokens))
    assert old.status_code == 401
    assert (await client.get("/api/account/passkeys", headers=bearer(renewed))).status_code == 200
    refresh = {"grant_type": "refresh_token", "refresh_token": app_tokens["refresh_token"]}
    assert (await client.post("/api/auth/token", data=refresh)).json() == {
        "error": "invalid_grant"
    }


@needs_passkey
async def test_reauth_renews_the_web_session_in_its_cookie(
    client: AsyncClient, session: AsyncSession, account: Account, passkey: Authenticator
) -> None:
    """The web authenticates again with its passkey: a new cookie."""
    options = await client.post("/api/auth/passkey/options")
    signed = passkey.sign(options.json()["challenge"], account.user_handle)
    login = await client.post("/api/auth/passkey/cookie", json=signed)
    cookie = SimpleCookie(login.headers["set-cookie"])[sessions.COOKIE].value
    await age(session, timedelta(minutes=10))
    headers = {"Cookie": f"{sessions.COOKIE}={cookie}", "Origin": "https://test"}
    options = await client.post("/api/auth/reauth/options", headers=headers)
    signed = passkey.sign(options.json()["challenge"], account.user_handle)
    response = await client.post("/api/auth/reauth/passkey", json=signed, headers=headers)
    assert response.status_code == 204
    renewed = SimpleCookie(response.headers["set-cookie"])[sessions.COOKIE].value
    assert renewed != cookie
    assert (await client.get("/api/account/passkeys", headers=headers)).status_code == 401
    headers["Cookie"] = f"{sessions.COOKIE}={renewed}"
    assert (await client.get("/api/account/passkeys", headers=headers)).status_code == 200


@needs_passkey
async def test_reauth_with_the_passkey_of_another_account_is_refused(
    client: AsyncClient, session: AsyncSession, account: Account, app_tokens: dict[str, str]
) -> None:
    """A passkey of another account does not authenticate this one."""
    other = Account(email="otra@example.com", role=Role.USER, language="es")
    session.add(other)
    await session.flush()
    authenticator = Authenticator()
    await register(session, other, authenticator)
    assert (await reauth(client, app_tokens, authenticator, other)).status_code == 403


@needs_passkey
async def test_changes_need_a_reauth_within_5_minutes(
    client: AsyncClient,
    session: AsyncSession,
    account: Account,
    passkey: Authenticator,
    app_tokens: dict[str, str],
) -> None:
    """A session that authenticated over 5 minutes ago is refused."""
    await age(session, timedelta(minutes=5, seconds=5))
    answers = [
        await link(client, app_tokens, Authenticator(), uuid4()),
        await client.delete(f"/api/account/passkeys/{uuid4()}", headers=bearer(app_tokens)),
        await client.put(
            "/api/account/email",
            json={"email": EMAIL, "code": "123456"},
            headers=bearer(app_tokens),
        ),
        await client.put(
            "/api/account/phone",
            json={"phone": PHONE, "code": "123456"},
            headers=bearer(app_tokens),
        ),
    ]
    for response in answers:
        assert response.status_code == 403
        assert response.json()["type"] == errors.REAUTHENTICATION_REQUIRED.uri
    await age(session, timedelta(minutes=4, seconds=55))
    assert (await link(client, app_tokens, Authenticator(), uuid4())).status_code == 201


@needs_passkey
async def test_link_is_idempotent_and_notifies_every_address(
    client: AsyncClient,
    session: AsyncSession,
    account: Account,
    passkey: Authenticator,
    app_tokens: dict[str, str],
    sent: list[httpx.Request],
) -> None:
    """A PUT creates the passkey; repeated, it answers the same one.

    The options exclude the passkeys of the account, and the link
    notifies the email and the phone, with what to do and the contact.
    """
    options = await client.post("/api/account/passkeys/options", headers=bearer(app_tokens))
    excluded = options.json()["excludeCredentials"]
    assert [base64url_to_bytes(item["id"]) for item in excluded] == [passkey.credential_id]
    assert (
        options.json()["user"]["id"]
        == passkey.sign("x", account.user_handle)["response"]["userHandle"]
    )
    laptop, passkey_id = Authenticator(), uuid4()
    response = await link(client, app_tokens, laptop, passkey_id)
    assert response.status_code == 201
    view = response.json()
    assert (view["id"], view["name"], view["lastUsedAt"]) == (str(passkey_id), "Laptop", None)
    assert sorted(recipients(sent)) == sorted([PHONE, EMAIL])
    for request in sent:
        text = body(request).get("text") or body(request)["body"]
        assert "Laptop" in text
        assert settings.contact in text
        assert "bórrala" in text
    again = await link(client, app_tokens, laptop, passkey_id)
    assert (again.status_code, again.json()) == (200, view)
    assert (await link(client, app_tokens, Authenticator(), passkey_id)).status_code == 409
    assert len(sent) == 2
    events = list(
        await session.scalars(sa.select(EventLog).where(EventLog.action == "sensitive_create"))
    )
    assert [(row.target_id, str(row.ip_address)) for row in events] == [
        (str(passkey_id), "127.0.0.1")
    ]
    linked = await session.get_one(Passkey, passkey_id)
    assert linked.created_at == linked.changed_at


@needs_passkey
async def test_link_refuses_the_options_of_another_account(
    client: AsyncClient, account: Account, app_tokens: dict[str, str]
) -> None:
    """The challenge of a registration keeps the handle it was for."""
    options = await client.post("/api/auth/register/options", json={"email": "x@example.com"})
    credential = Authenticator().create(options.json()["challenge"])
    response = await client.put(
        f"/api/account/passkeys/{uuid4()}",
        json={"name": "Laptop", "credential": credential},
        headers=bearer(app_tokens),
    )
    assert response.status_code == 400


@needs_passkey
async def test_passkeys_are_listed_and_deleted(
    client: AsyncClient,
    session: AsyncSession,
    account: Account,
    passkey: Authenticator,
    app_tokens: dict[str, str],
    sent: list[httpx.Request],
) -> None:
    """The holder sees each passkey with its name and last use.

    Deleting one notifies every address; another account's is a 404.
    """
    await link(client, app_tokens, Authenticator(), uuid4())
    sent.clear()
    first = await client.get("/api/account/passkeys?pageSize=1", headers=bearer(app_tokens))
    page = first.json()
    assert [item["name"] for item in page["items"]] == ["Phone"]
    assert set(page["items"][0]) == {"id", "name", "createdAt", "lastUsedAt", "disabledAt"}
    second = await client.get(
        f"/api/account/passkeys?pageSize=1&pageToken={page['nextPageToken']}",
        headers=bearer(app_tokens),
    )
    assert [item["name"] for item in second.json()["items"]] == ["Laptop"]
    phone_id = page["items"][0]["id"]
    response = await client.delete(f"/api/account/passkeys/{phone_id}", headers=bearer(app_tokens))
    assert response.status_code == 204
    assert await session.get(Passkey, UUID(phone_id)) is None
    assert sorted(recipients(sent)) == sorted([PHONE, EMAIL])
    assert "sensitive_delete" in await session.scalars(sa.select(EventLog.action))
    response = await client.delete(f"/api/account/passkeys/{phone_id}", headers=bearer(app_tokens))
    assert response.status_code == 404
    other = Account(email="otra@example.com", role=Role.USER, language="es")
    session.add(other)
    await session.flush()
    theirs = await register(session, other, Authenticator())
    response = await client.delete(
        f"/api/account/passkeys/{theirs.id}", headers=bearer(app_tokens)
    )
    assert response.status_code == 404
    assert await session.get(Passkey, theirs.id) is not None


async def test_email_changes_with_a_code_to_the_new_one(
    client: AsyncClient,
    session: AsyncSession,
    account: Account,
    app_tokens: dict[str, str],
    sent: list[httpx.Request],
) -> None:
    """The code goes to the new email; the old one gets a notice."""
    new = "nueva@example.com"
    response = await client.post(
        "/api/account/email/code", json={"email": new}, headers=bearer(app_tokens)
    )
    assert response.status_code == 204
    assert recipients(sent) == [new]
    code = re.search(r"\d{6}", body(sent[0])["text"])
    assert code is not None
    wrong = f"{(int(code[0]) + 1) % 10**6:06d}"
    change = {"email": new, "code": wrong}
    response = await client.put("/api/account/email", json=change, headers=bearer(app_tokens))
    assert (response.status_code, response.json()["type"]) == (400, errors.INVALID_CODE.uri)
    change["code"] = code[0]
    response = await client.put("/api/account/email", json=change, headers=bearer(app_tokens))
    assert response.status_code == 204
    await session.refresh(account)
    assert account.email == new
    assert sorted(recipients(sent[1:])) == sorted([PHONE, EMAIL, new])
    assert "user_updated" in await session.scalars(sa.select(EventLog.action))


async def test_email_or_phone_of_another_account_is_a_409(
    client: AsyncClient, session: AsyncSession, account: Account, app_tokens: dict[str, str]
) -> None:
    """An email or a phone that another account has is a 409."""
    session.add(
        Account(email="otra@example.com", phone="+522221234567", role=Role.USER, language="es")
    )
    await session.flush()
    email = await client.post(
        "/api/account/email/code", json={"email": "otra@example.com"}, headers=bearer(app_tokens)
    )
    phone = await client.post(
        "/api/account/phone/code",
        json={"phone": "+522221234567"},
        headers={**bearer(app_tokens), "Host": HOST},
    )
    assert (email.status_code, phone.status_code) == (409, 409)


async def test_phone_changes_with_an_sms_to_the_new_one(
    client: AsyncClient,
    session: AsyncSession,
    account: Account,
    app_tokens: dict[str, str],
    sent: list[httpx.Request],
) -> None:
    """The code goes by SMS to the new phone; the old one, a notice."""
    new = "+522221234567"
    headers = {**bearer(app_tokens), "Host": HOST}
    response = await client.post("/api/account/phone/code", json={"phone": new}, headers=headers)
    assert response.status_code == 204
    sms = body(sent[0])
    assert sms["to"] == new
    code = sms["body"].rsplit("#", 1)[1]
    assert sms["body"].endswith(f"@{HOST} #{code}")
    response = await client.put(
        "/api/account/phone", json={"phone": new, "code": code}, headers=headers
    )
    assert response.status_code == 204
    await session.refresh(account)
    assert account.phone == new
    assert sorted(recipients(sent[1:])) == sorted([PHONE, new, EMAIL])


async def test_email_change_codes_follow_the_limits(
    client: AsyncClient, account: Account, app_tokens: dict[str, str], clock: list[int]
) -> None:
    """The code of a new email waits its minute, like any code."""
    new = {"email": "nueva@example.com"}
    assert (
        await client.post("/api/account/email/code", json=new, headers=bearer(app_tokens))
    ).status_code == 204
    response = await client.post("/api/account/email/code", json=new, headers=bearer(app_tokens))
    assert response.status_code == 429
    clock[0] += 61_000
    assert (
        await client.post("/api/account/email/code", json=new, headers=bearer(app_tokens))
    ).status_code == 204


async def test_account_shows_its_authenticators_and_which_are_disabled(
    client: AsyncClient, session: AsyncSession, account: Account, app_tokens: dict[str, str]
) -> None:
    """The account shows its phone and its password, and each passkey.

    Each with whether it is disabled.
    """
    moment = datetime.now(UTC)
    session.add(Phone(account_id=account.id, disabled_at=moment))
    passkey = await register(session, account, Authenticator())
    await session.execute(sa.update(Password).values(disabled_at=moment))
    await session.execute(sa.update(Passkey).values(disabled_at=moment))
    response = await client.get("/api/account", headers=bearer(app_tokens))
    assert response.status_code == 200
    shown = response.json()
    assert set(shown) == {"id", "email", "phone", "role", "createdAt", "password"}
    assert (shown["id"], shown["email"], shown["role"]) == (str(account.id), EMAIL, "user")
    assert set(shown["phone"]) == {"number", "changedAt", "disabledAt"}
    assert (shown["phone"]["number"], shown["phone"]["disabledAt"] is None) == (PHONE, False)
    assert shown["password"]["disabledAt"] is not None
    if Method.PASSKEY in METHODS:
        listed = await client.get("/api/account/passkeys", headers=bearer(app_tokens))
        item = listed.json()["items"][0]
        assert (item["id"], item["disabledAt"] is not None) == (str(passkey.id), True)


@pytest.mark.skipif(
    not METHODS >= {Method.PASSWORD, Method.SMS}, reason="the product offers not both methods"
)
async def test_failures_list_each_failed_attempt_newest_first(
    client: AsyncClient, session: AsyncSession, account: Account, app_tokens: dict[str, str]
) -> None:
    """Each failure on the account, with what failed, its IP and agent.

    A wrong password, a wrong code of the SMS or of the recovery, and a
    refresh token used again; another account's are not shown.
    """
    session.add(Phone(account_id=account.id))
    other = Account(email="otra@example.com", role=Role.USER, language="es")
    session.add(other)
    await session.flush()
    session.add(Password(account_id=other.id, hash=passwords.hash_password(PASSWORD)))
    await session.flush()
    agent = {"User-Agent": "Mozilla/5.0"}
    wrong = {"email": EMAIL, "password": "Wrong horse battery"}
    await client.post("/api/auth/password/token", json=wrong, headers=agent)
    theirs = {"email": "otra@example.com", "password": "Wrong horse battery"}
    await client.post("/api/auth/password/token", json=theirs, headers=agent)
    await client.post("/api/auth/sms/token", json={"phone": PHONE, "code": "123456"})
    recovery = {"email": EMAIL, "code": "123456", "password": "Staple of a purple ocean"}
    await client.post("/api/auth/recovery/password", json=recovery)
    first = {"grant_type": "refresh_token", "refresh_token": app_tokens["refresh_token"]}
    second = (await client.post("/api/auth/token", data=first)).json()
    third = {"grant_type": "refresh_token", "refresh_token": second["refresh_token"]}
    await client.post("/api/auth/token", data=third)
    # The first secret is neither the current one nor the previous one.
    assert (await client.post("/api/auth/token", data=first)).status_code == 400
    fresh = await sessions.open_app(session, account, Client("127.0.0.1", "test"), "es")
    headers = {"Authorization": f"Bearer {fresh.access_token}"}
    response = await client.get("/api/account/failures?pageSize=3", headers=headers)
    assert response.status_code == 200
    page = response.json()
    assert [item["credential"] for item in page["items"]] == [
        "refresh_token",
        "email_recovery",
        "sms_code",
    ]
    assert set(page["items"][0]) == {
        "occurredAt",
        "credential",
        "passkeyId",
        "ipAddress",
        "userAgent",
    }
    following = await client.get(
        f"/api/account/failures?pageToken={page['nextPageToken']}", headers=headers
    )
    rest = following.json()
    assert [item["credential"] for item in rest["items"]] == ["password"]
    assert rest["items"][0]["ipAddress"] == "127.0.0.1"
    assert rest["items"][0]["userAgent"] == "Mozilla/5.0"
    assert rest["nextPageToken"] == ""


@needs_passkey
async def test_failures_name_the_passkey(
    client: AsyncClient,
    session: AsyncSession,
    account: Account,
    passkey: Authenticator,
    app_tokens: dict[str, str],
) -> None:
    """A failed assertion is shown with the ID of its passkey."""
    options = await client.post("/api/auth/passkey/options")
    signed = passkey.sign(options.json()["challenge"], account.user_handle, rp_id="evil.example")
    assert (await client.post("/api/auth/passkey/token", json=signed)).status_code == 401
    response = await client.get("/api/account/failures", headers=bearer(app_tokens))
    item = response.json()["items"][0]
    row = (await session.scalars(sa.select(Passkey))).one()
    assert (item["credential"], item["passkeyId"]) == ("passkey", str(row.id))


@needs_passkey
async def test_enabling_a_passkey_binds_it_again(
    client: AsyncClient,
    session: AsyncSession,
    account: Account,
    app_tokens: dict[str, str],
    sent: list[httpx.Request],
) -> None:
    """A fresh authentication enables it, with no failures and a notice.

    One that is not disabled stays; another account's is a 404.
    """
    row = await register(session, account, Authenticator())
    moment = datetime.now(UTC) - timedelta(hours=1)
    await session.execute(
        sa.update(Passkey).values(
            failures=100, retry_at=moment, disabled_at=moment, changed_at=moment
        )
    )
    path = f"/api/account/passkeys/{row.id}/enable"
    await age(session, timedelta(minutes=6))
    stale = await client.post(path, headers=bearer(app_tokens))
    assert stale.json()["type"] == errors.REAUTHENTICATION_REQUIRED.uri
    await age(session, timedelta(0))
    assert (await client.post(path, headers=bearer(app_tokens))).status_code == 204
    await session.refresh(row)
    assert (row.failures, row.retry_at, row.disabled_at) == (0, None, None)
    assert row.changed_at > moment
    assert sorted(recipients(sent)) == sorted([EMAIL, PHONE])
    assert "sensitive_update" in await session.scalars(sa.select(EventLog.action))
    assert (await client.post(path, headers=bearer(app_tokens))).status_code == 204
    assert len(sent) == 2
    other = Account(email="otra@example.com", role=Role.USER, language="es")
    session.add(other)
    await session.flush()
    theirs = await register(session, other, Authenticator())
    await session.execute(sa.update(Passkey).values(disabled_at=moment))
    response = await client.post(
        f"/api/account/passkeys/{theirs.id}/enable", headers=bearer(app_tokens)
    )
    assert response.status_code == 404
    await session.refresh(theirs)
    assert theirs.disabled_at is not None


@pytest.mark.skipif(Method.SMS not in METHODS, reason="the product offers no SMS code")
async def test_enabling_the_phone_binds_it_again(
    client: AsyncClient,
    session: AsyncSession,
    account: Account,
    app_tokens: dict[str, str],
    sent: list[httpx.Request],
) -> None:
    """The phone signs in with its code again; without one, a 409."""
    moment = datetime.now(UTC) - timedelta(hours=1)
    row = Phone(account_id=account.id, failures=100, disabled_at=moment, changed_at=moment)
    session.add(row)
    await session.flush()
    await age(session, timedelta(minutes=6))
    stale = await client.post("/api/account/phone/enable", headers=bearer(app_tokens))
    assert stale.json()["type"] == errors.REAUTHENTICATION_REQUIRED.uri
    await age(session, timedelta(0))
    response = await client.post("/api/account/phone/enable", headers=bearer(app_tokens))
    assert response.status_code == 204
    await session.refresh(row)
    assert (row.failures, row.disabled_at) == (0, None)
    assert row.changed_at > moment
    assert sorted(recipients(sent)) == sorted([EMAIL, PHONE])
    assert (
        await client.post("/api/account/phone/enable", headers=bearer(app_tokens))
    ).status_code == 204
    assert len(sent) == 2
    account.phone = None
    await session.flush()
    response = await client.post("/api/account/phone/enable", headers=bearer(app_tokens))
    assert response.status_code == 409


async def test_sessions_are_listed_with_their_device(
    client: AsyncClient, session: AsyncSession, account: Account, app_tokens: dict[str, str]
) -> None:
    """Each session by its kind, its agent and its use, newest first."""
    _, web_id = await sessions.open_web(session, account, Client("127.0.0.1", "Mozilla/5.0"), "es")
    later = datetime.now(UTC) + timedelta(minutes=1)
    await session.execute(
        sa.update(AccountSession).where(AccountSession.id == web_id).values(created_at=later)
    )
    first = await client.get("/api/account/sessions?pageSize=1", headers=bearer(app_tokens))
    assert first.status_code == 200
    item = first.json()["items"][0]
    assert set(item) == {"id", "kind", "userAgent", "createdAt", "lastUsedAt", "current"}
    assert (item["kind"], item["userAgent"], item["current"]) == ("web", "Mozilla/5.0", False)
    token = first.json()["nextPageToken"]
    second = await client.get(
        f"/api/account/sessions?pageToken={token}", headers=bearer(app_tokens)
    )
    item = second.json()["items"][0]
    assert (item["kind"], item["userAgent"], item["current"]) == ("app", "test", True)


async def test_holder_closes_one_session(
    client: AsyncClient, session: AsyncSession, account: Account, app_tokens: dict[str, str]
) -> None:
    """After authenticating again; another account's is a 404.

    Closing the one that calls signs it out.
    """
    token, other_id = await sessions.open_web(session, account, Client(None, None), "es")
    stranger = Account(email="otra@example.com", role=Role.USER, language="es")
    session.add(stranger)
    await session.flush()
    _, theirs = await sessions.open_web(session, stranger, Client(None, None), "es")
    await session.flush()
    path = f"/api/account/sessions/{other_id}"
    await age(session, timedelta(minutes=6))
    stale = await client.delete(path, headers=bearer(app_tokens))
    assert stale.json()["type"] == errors.REAUTHENTICATION_REQUIRED.uri
    await age(session, timedelta(0))
    assert (await client.delete(path, headers=bearer(app_tokens))).status_code == 204
    cookie = {"Cookie": f"{sessions.COOKIE}={token}"}
    assert (await client.get("/api/account", headers=cookie)).status_code == 401
    response = await client.delete(f"/api/account/sessions/{theirs}", headers=bearer(app_tokens))
    assert response.status_code == 404
    found = sa.select(sa.func.count()).where(AccountSession.id == theirs)
    assert await session.scalar(found) == 1
    own = (await client.get("/api/account/sessions", headers=bearer(app_tokens))).json()
    own_id = own["items"][0]["id"]
    response = await client.delete(f"/api/account/sessions/{own_id}", headers=bearer(app_tokens))
    assert response.status_code == 204
    assert (await client.get("/api/account", headers=bearer(app_tokens))).status_code == 401


async def test_closing_the_web_session_that_calls_clears_its_cookie(
    client: AsyncClient, session: AsyncSession, account: Account
) -> None:
    """Closing it there is signing out."""
    token, session_id = await sessions.open_web(session, account, Client(None, None), "es")
    await session.flush()
    headers = {"Cookie": f"{sessions.COOKIE}={token}", "Origin": "https://test"}
    response = await client.delete(f"/api/account/sessions/{session_id}", headers=headers)
    assert response.status_code == 204
    assert SimpleCookie(response.headers["set-cookie"])[sessions.COOKIE]["max-age"] == "0"


async def test_holder_deletes_the_account(
    client: AsyncClient, session: AsyncSession, account: Account, sent: list[httpx.Request]
) -> None:
    """After authenticating again, with the web cookie gone.

    Its authenticators and sessions go with it, and every address hears.
    """
    session.add(Phone(account_id=account.id))
    await register(session, account, Authenticator())
    token, web_id = await sessions.open_web(session, account, Client(None, None), "es")
    await sessions.open_app(session, account, Client(None, None), "es")
    # A last use that the web writes again in the same request.
    stale_use = datetime.now(UTC) - timedelta(minutes=20)
    await session.execute(
        sa.update(AccountSession).where(AccountSession.id == web_id).values(last_used_at=stale_use)
    )
    headers = {"Cookie": f"{sessions.COOKIE}={token}", "Origin": "https://test"}
    await age(session, timedelta(minutes=6))
    stale = await client.delete("/api/account", headers=headers)
    assert stale.json()["type"] == errors.REAUTHENTICATION_REQUIRED.uri
    await age(session, timedelta(0))
    response = await client.delete("/api/account", headers=headers)
    assert response.status_code == 204
    cookies = [SimpleCookie(value) for value in response.headers.get_list("set-cookie")]
    assert cookies[-1][sessions.COOKIE]["max-age"] == "0"
    for model in (Account, AccountSession, Passkey, Password, Phone):
        assert await session.scalar(sa.select(sa.func.count()).select_from(model)) == 0
    assert sorted(recipients(sent)) == sorted([EMAIL, PHONE])
    deleted = (
        await session.scalars(sa.select(EventLog).where(EventLog.action == "user_deleted"))
    ).one()
    assert deleted.level == "warn"
    assert deleted.target_id == str(deleted.actor_id)


async def test_superadmin_does_not_delete_its_own_account(
    client: AsyncClient, session: AsyncSession, account: Account, app_tokens: dict[str, str]
) -> None:
    """Another superadmin deletes it."""
    account.role = Role.SUPERADMIN
    await session.flush()
    assert (await client.delete("/api/account", headers=bearer(app_tokens))).status_code == 403
    found = sa.select(sa.func.count()).where(Account.id == account.id)
    assert await session.scalar(found) == 1


@pytest.mark.parametrize("address", list(Address))
async def test_new_address_starts_its_recovery_with_no_failures(
    client: AsyncClient,
    session: AsyncSession,
    account: Account,
    app_tokens: dict[str, str],
    sent: list[httpx.Request],
    address: Address,
) -> None:
    """A new email or phone recovers, if the old one was disabled."""
    session.add(Phone(account_id=account.id))
    way = RecoveryAddress(
        account_id=account.id, address=address, failures=100, disabled_at=datetime.now(UTC)
    )
    session.add(way)
    await session.flush()
    new = (
        {"email": "nueva@example.com"} if address == Address.EMAIL else {"phone": "+522221234567"}
    )
    headers = {**bearer(app_tokens), "Host": HOST}
    await client.post(f"/api/account/{address}/code", json=new, headers=headers)
    message = body(sent[0])
    code = re.search(r"\d{6}", message.get("text") or message["body"].rsplit("#", 1)[1])
    assert code is not None
    change = {**new, "code": code[0]}
    response = await client.put(f"/api/account/{address}", json=change, headers=headers)
    assert response.status_code == 204
    await session.refresh(way)
    assert (way.failures, way.disabled_at) == (0, None)
