"""The account of the session, and the notices of its changes.

Authenticating again, its passkeys, its email and its phone.
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
from app.enums import Role
from app.models.account.account import Account
from app.models.account.account_session import AccountSession
from app.models.account.passkey import Passkey
from app.models.account.password import Password
from app.models.event.event_log import EventLog
from app.services import limits, passwords, sessions
from tests.authenticator import Authenticator, register

EMAIL = "ana@example.com"
PHONE = "+56221234567"
PASSWORD = "Correct horse battery"
HOST = f"app.{settings.domain}"


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
async def app_tokens(client: AsyncClient, account: Account) -> dict[str, str]:
    """Sign in an app with the password and return its tokens."""
    response = await client.post(
        "/api/auth/password/token", json={"email": EMAIL, "password": PASSWORD}
    )
    found: dict[str, str] = response.json()
    return found


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


async def test_reauth_renews_the_web_session_in_its_cookie(
    client: AsyncClient, session: AsyncSession, account: Account
) -> None:
    """The web authenticates again with the password: a new cookie."""
    login = await client.post(
        "/api/auth/password/cookie", json={"email": EMAIL, "password": PASSWORD}
    )
    cookie = SimpleCookie(login.headers["set-cookie"])[sessions.COOKIE].value
    await age(session, timedelta(minutes=10))
    headers = {"Cookie": f"{sessions.COOKIE}={cookie}", "Origin": "https://test"}
    response = await client.post(
        "/api/auth/reauth/password", json={"password": PASSWORD}, headers=headers
    )
    assert response.status_code == 204
    renewed = SimpleCookie(response.headers["set-cookie"])[sessions.COOKIE].value
    assert renewed != cookie
    assert (await client.get("/api/account/passkeys", headers=headers)).status_code == 401
    headers["Cookie"] = f"{sessions.COOKIE}={renewed}"
    assert (await client.get("/api/account/passkeys", headers=headers)).status_code == 200
    wrong = await client.post(
        "/api/auth/reauth/password", json={"password": "wrong"}, headers=headers
    )
    assert wrong.status_code == 401


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
    assert set(page["items"][0]) == {"id", "name", "createdAt", "lastUsedAt"}
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
