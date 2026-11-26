"""What a superadmin does to the other accounts."""

import json
import re
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import httpx
import pytest
import sqlalchemy as sa
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app import errors
from app.config import settings
from app.enums import Address, Method, Role
from app.methods import METHODS
from app.models.account.account import Account
from app.models.account.account_session import AccountSession
from app.models.account.passkey import Passkey
from app.models.account.password import Password
from app.models.account.phone import Phone
from app.models.account.recovery import Recovery
from app.models.account.recovery_address import RecoveryAddress
from app.models.account.recovery_code import RecoveryCode
from app.models.event.event_log import EventLog
from app.services import authorization, events, passwords, recovery, sessions
from app.services.sessions import Client
from tests.authenticator import UP, Authenticator, register

EMAIL = "ana@example.com"
PHONE = "+56221234567"
NEW_EMAIL = "nueva@example.com"
NEW_PHONE = "+522221234567"
PASSWORD = "Correct horse battery"
HOST = f"app.{settings.domain}"
CLIENT = Client("127.0.0.1", "test")
needs_recovery = pytest.mark.skipif(
    not METHODS & {Method.PASSKEY, Method.PASSWORD}, reason="the product recovers no account"
)
needs_passkey = pytest.mark.skipif(
    Method.PASSKEY not in METHODS, reason="the product offers no passkey"
)


async def opened(session: AsyncSession, account: Account) -> dict[str, str]:
    """Open an app session as a login would; return its header."""
    issued = await sessions.open_app(session, account, CLIENT, "es")
    await session.flush()
    return {"Authorization": f"Bearer {issued.access_token}"}


@pytest.fixture
async def superadmin(session: AsyncSession) -> Account:
    """Create the superadmin that calls."""
    row = Account(email="dueno@example.com", role=Role.SUPERADMIN, language="es")
    session.add(row)
    await session.flush()
    return row


@pytest.fixture
async def headers(session: AsyncSession, superadmin: Account) -> dict[str, str]:
    """Present the session of the superadmin."""
    return await opened(session, superadmin)


async def holder(session: AsyncSession, role: Role) -> Account:
    """Create an account with an email, a phone and a password."""
    row = Account(email=EMAIL, phone=PHONE, role=role, language="es")
    session.add(row)
    await session.flush()
    session.add(Password(account_id=row.id, hash=passwords.hash_password(PASSWORD)))
    session.add(Phone(account_id=row.id))
    await session.flush()
    return row


@pytest.fixture
async def account(session: AsyncSession) -> Account:
    """Create the account of a user."""
    return await holder(session, Role.USER)


def changes(account_id: object) -> list[tuple[str, str, dict[str, str] | None]]:
    """List each change of an account: method, path and body."""
    path = f"/api/accounts/{account_id}"
    return [
        ("POST", f"{path}/disable", None),
        ("POST", f"{path}/enable", None),
        ("PUT", f"{path}/email", {"email": NEW_EMAIL}),
        ("PUT", f"{path}/phone", {"phone": NEW_PHONE}),
        ("PUT", f"{path}/role", {"role": "superadmin"}),
        ("DELETE", f"{path}/sessions", None),
        ("DELETE", path, None),
    ]


def body(request: httpx.Request) -> dict[str, Any]:
    """Read the JSON a request sent to Equipaggio."""
    found: dict[str, Any] = json.loads(request.content)
    return found


def to(sent: list[httpx.Request]) -> set[str]:
    """Return who the messages went to."""
    return {body(request)["to"] for request in sent}


def code_in(request: httpx.Request) -> str:
    """Read the code of an email or an SMS."""
    found = re.search(r"\d{6}", body(request).get("text") or body(request)["body"])
    assert found is not None
    return found[0]


async def count(session: AsyncSession, model: type[Any], account: Account) -> int:
    """Count the rows of an account."""
    query = sa.select(sa.func.count()).where(model.account_id == account.id)
    return await session.scalar(query) or 0


async def logged(session: AsyncSession, action: str) -> EventLog:
    """Return the only event of an action."""
    return (await session.scalars(sa.select(EventLog).where(EventLog.action == action))).one()


async def ask(client: AsyncClient, **identifier: str) -> Response:
    """Ask for the code to recover."""
    return await client.post("/api/auth/recovery/code", json=identifier, headers={"Host": HOST})


async def age(session: AsyncSession, span: timedelta) -> None:
    """Move the last authentication of every session to the past."""
    moment = datetime.now(UTC) - span
    await session.execute(sa.update(AccountSession).values(authenticated_at=moment))


async def test_only_a_superadmin_manages_the_accounts(
    client: AsyncClient,
    session: AsyncSession,
    account: Account,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Another account gets 403 on every route, with its event."""
    found: list[EventLog] = []

    async def record(row: EventLog) -> None:
        """Keep an event that goes in its own transaction."""
        found.append(row)

    monkeypatch.setattr(events, "record", record)
    theirs = await opened(session, account)
    other = Account(email="otra@example.com", role=Role.USER, language="es")
    session.add(other)
    await session.flush()
    routes = [
        ("GET", "/api/accounts", None),
        ("DELETE", "/api/accounts/sessions", None),
        *changes(other.id),
    ]
    for method, path, sent in routes:
        response = await client.request(method, path, json=sent, headers=theirs)
        assert response.status_code == 403, path
    assert len(found) == len(routes)
    assert {(row.action, row.level, row.actor_id) for row in found} == {
        ("authz_fail", "critical", account.id)
    }
    await session.refresh(other)
    assert (other.disabled_at, other.email) == (None, "otra@example.com")


async def test_superadmin_changes_ask_a_fresh_authentication(
    client: AsyncClient, session: AsyncSession, account: Account, headers: dict[str, str]
) -> None:
    """Each change asks it; seeing the accounts does not."""
    await age(session, timedelta(minutes=6))
    for method, path, sent in [("DELETE", "/api/accounts/sessions", None), *changes(account.id)]:
        response = await client.request(method, path, json=sent, headers=headers)
        assert response.status_code == 403, path
        assert response.json()["type"] == errors.REAUTHENTICATION_REQUIRED.uri, path
    assert (await client.get("/api/accounts", headers=headers)).status_code == 200


async def test_superadmin_does_not_act_on_itself(
    client: AsyncClient, session: AsyncSession, superadmin: Account, headers: dict[str, str]
) -> None:
    """Its own account is a 403, and an unknown one a 404."""
    for method, path, sent in changes(superadmin.id):
        response = await client.request(method, path, json=sent, headers=headers)
        assert response.status_code == 403, path
    for method, path, sent in changes(uuid4()):
        response = await client.request(method, path, json=sent, headers=headers)
        assert response.status_code == 404, path
    await session.refresh(superadmin)
    assert (superadmin.disabled_at, superadmin.email) == (None, "dueno@example.com")


async def test_superadmin_finds_the_accounts(
    client: AsyncClient, session: AsyncSession, account: Account, headers: dict[str, str]
) -> None:
    """Oldest first, in pages, and by an exact email or phone.

    The token keeps its filter.
    """
    old = datetime.now(UTC) - timedelta(days=1)
    await session.execute(
        sa.update(Account).where(Account.id == account.id).values(created_at=old)
    )
    first = (await client.get("/api/accounts?pageSize=1", headers=headers)).json()
    assert [item["email"] for item in first["items"]] == [EMAIL]
    assert set(first["items"][0]) == {"id", "email", "phone", "role", "createdAt", "disabledAt"}
    token = first["nextPageToken"]
    second = await client.get(f"/api/accounts?pageToken={token}", headers=headers)
    assert [item["email"] for item in second.json()["items"]] == ["dueno@example.com"]
    for filters in ({"email": EMAIL.upper()}, {"phone": PHONE}):
        found = await client.get("/api/accounts", params=filters, headers=headers)
        assert [item["id"] for item in found.json()["items"]] == [str(account.id)]
    none = await client.get("/api/accounts", params={"email": NEW_EMAIL}, headers=headers)
    assert none.json() == {"items": [], "nextPageToken": ""}
    moved = await client.get(
        "/api/accounts", params={"email": EMAIL, "pageToken": token}, headers=headers
    )
    assert moved.status_code == 422


async def fill(session: AsyncSession, account: Account) -> None:
    """Give an account everything that disabling takes from it."""
    await register(session, account, Authenticator())
    session.add(RecoveryCode(account_id=account.id, hash="hash"))
    session.add(RecoveryAddress(account_id=account.id, address=Address.EMAIL, failures=3))
    session.add(
        Recovery(
            account_id=account.id,
            address=Address.EMAIL,
            applies_at=datetime.now(UTC),
            password_hash="hash",
        )
    )
    await session.flush()


LOST = (AccountSession, Passkey, Password, RecoveryCode, RecoveryAddress, Recovery)


async def test_disabling_takes_the_authenticators_and_the_sessions(
    client: AsyncClient,
    session: AsyncSession,
    account: Account,
    superadmin: Account,
    headers: dict[str, str],
    sent: list[httpx.Request],
) -> None:
    """It keeps the email and the phone, and every address hears.

    Enabling it returns nothing of what it lost.
    """
    await fill(session, account)
    theirs = await opened(session, account)
    path = f"/api/accounts/{account.id}"
    assert (await client.post(f"{path}/disable", headers=headers)).status_code == 204
    assert [await count(session, model, account) for model in LOST] == [0] * len(LOST)
    await session.refresh(account)
    assert account.disabled_at is not None
    assert (account.email, account.phone) == (EMAIL, PHONE)
    assert (await client.get("/api/account", headers=theirs)).status_code == 401
    assert to(sent) == {EMAIL, PHONE}
    archived = await logged(session, "user_archived")
    admin = await logged(session, "authz_admin")
    for row in (archived, admin):
        assert (row.level, row.actor_id) == ("warn", superadmin.id)
        assert row.target_id == str(account.id)
    moment = account.disabled_at
    assert (await client.post(f"{path}/disable", headers=headers)).status_code == 204
    await session.refresh(account)
    assert account.disabled_at == moment
    assert len(sent) == 2
    assert (await client.post(f"{path}/enable", headers=headers)).status_code == 204
    await session.refresh(account)
    assert account.disabled_at is None
    assert [await count(session, model, account) for model in LOST] == [0] * len(LOST)
    assert await count(session, AccountSession, superadmin) == 1


async def test_disabled_account_opens_no_session(
    client: AsyncClient, session: AsyncSession, account: Account
) -> None:
    """A session that a race left is no session, and opens none."""
    issued = await sessions.open_app(session, account, CLIENT, "es")
    cookie, _ = await sessions.open_web(session, account, CLIENT, "es")
    account.disabled_at = datetime.now(UTC)
    await session.flush()
    bearer = {"Authorization": f"Bearer {issued.access_token}"}
    assert (await client.get("/api/account", headers=bearer)).status_code == 401
    web = {"Cookie": f"{sessions.COOKIE}={cookie}"}
    assert (await client.get("/api/account", headers=web)).status_code == 401
    form = {"grant_type": "refresh_token", "refresh_token": issued.refresh_token}
    refreshed = await client.post("/api/auth/token", data=form)
    assert (refreshed.status_code, refreshed.json()) == (400, {"error": "invalid_grant"})
    with pytest.raises(errors.AppError):
        await sessions.open_web(session, account, CLIENT, "es")
    with pytest.raises(errors.AppError):
        await sessions.open_app(session, account, CLIENT, "es")


@needs_passkey
@pytest.mark.parametrize("ending", ["disabled", "deleted"])
async def test_code_of_an_account_that_ended_is_invalid_grant(
    client: AsyncClient,
    session: AsyncSession,
    account: Account,
    monkeypatch: pytest.MonkeyPatch,
    ending: str,
) -> None:
    """The authorization code got before does not open a session."""
    record = {
        "account_id": str(account.id),
        "client_id": "web",
        "redirect_uri": "https://x/y",
        "redirect_given": True,
        "code_challenge": authorization.challenge_of("v" * 43),
        "session_id": None,
    }
    key = f"auth:code:{authorization.digest('code')}"
    await authorization.store.client.set(key, json.dumps(record))
    if ending == "deleted":
        await session.delete(account)
    else:
        account.disabled_at = datetime.now(UTC)
    await session.flush()
    form = {
        "grant_type": "authorization_code",
        "code": "code",
        "client_id": "web",
        "redirect_uri": "https://x/y",
        "code_verifier": "v" * 43,
    }
    response = await client.post("/api/auth/token", data=form)
    assert (response.status_code, response.json()) == (400, {"error": "invalid_grant"})


@needs_recovery
async def test_disabled_account_recovers_nothing(
    client: AsyncClient, session: AsyncSession, account: Account, sent: list[httpx.Request]
) -> None:
    """Asking or presenting the code is a 403 of its type.

    A recovery that a race left is dropped, and enabled it recovers.
    """
    account.disabled_at = datetime.now(UTC)
    session.add(
        Recovery(
            account_id=account.id,
            address=Address.EMAIL,
            applies_at=datetime.now(UTC),
            password_hash="hash",
        )
    )
    await session.flush()
    answers = [await ask(client, email=EMAIL)]
    presented = {"email": EMAIL, "code": "123456", "password": "Staple of a purple ocean"}
    if Method.PASSWORD in METHODS:
        answers.append(await client.post("/api/auth/recovery/password", json=presented))
    for response in answers:
        assert response.status_code == 403
        assert response.json()["type"] == errors.ACCOUNT_DISABLED.uri
    await recovery.apply_due()
    assert await count(session, Recovery, account) == 0
    stored = await session.scalar(sa.select(Password.hash))
    assert stored != "hash"
    assert sent == []
    account.disabled_at = None
    await session.flush()
    assert (await ask(client, email=EMAIL)).status_code == 204


@pytest.mark.skipif(Method.SMS not in METHODS, reason="the product offers no SMS code")
async def test_disabled_account_gets_no_code_to_sign_in(
    client: AsyncClient, session: AsyncSession, account: Account, sent: list[httpx.Request]
) -> None:
    """Asking or presenting the code of the SMS is a 403 of its type."""
    account.disabled_at = datetime.now(UTC)
    await session.flush()
    asked: dict[str, str] = {}
    for path, presented in (("code", asked), ("token", {"code": "123456"})):
        response = await client.post(
            f"/api/auth/sms/{path}", json={"phone": PHONE, **presented}, headers={"Host": HOST}
        )
        assert response.status_code == 403
        assert response.json()["type"] == errors.ACCOUNT_DISABLED.uri
    assert sent == []
    row = await session.get_one(Phone, account.id)
    await session.refresh(row)
    assert row.failures == 0
    account.disabled_at = None
    await session.flush()
    response = await client.post(
        "/api/auth/sms/code", json={"phone": PHONE}, headers={"Host": HOST}
    )
    assert response.status_code == 204


async def test_superadmin_deletes_another_account(
    client: AsyncClient,
    session: AsyncSession,
    account: Account,
    superadmin: Account,
    headers: dict[str, str],
    sent: list[httpx.Request],
) -> None:
    """Its rows go, every address hears, and the events name who did."""
    await fill(session, account)
    await opened(session, account)
    response = await client.delete(f"/api/accounts/{account.id}", headers=headers)
    assert response.status_code == 204
    found = sa.select(sa.func.count()).where(Account.id == account.id)
    assert await session.scalar(found) == 0
    assert [await count(session, model, account) for model in LOST] == [0] * len(LOST)
    assert to(sent) == {EMAIL, PHONE}
    for action in ("user_deleted", "authz_admin"):
        row = await logged(session, action)
        assert (row.actor_id, row.target_id) == (superadmin.id, str(account.id))


@pytest.mark.parametrize(
    ("address", "old", "new"), [("email", EMAIL, NEW_EMAIL), ("phone", PHONE, NEW_PHONE)]
)
async def test_superadmin_gives_an_address_the_holder_has(
    client: AsyncClient,
    session: AsyncSession,
    account: Account,
    superadmin: Account,
    headers: dict[str, str],
    sent: list[httpx.Request],
    address: str,
    old: str,
    new: str,
) -> None:
    """Without a code; the old address hears, and the new one recovers.

    Repeated it answers the same, and one of another account is a 409.
    """
    moment = datetime.now(UTC)
    way = RecoveryAddress(
        account_id=account.id, address=Address(address), failures=100, disabled_at=moment
    )
    session.add(way)
    await session.execute(sa.update(Phone).values(failures=100, disabled_at=moment))
    await session.flush()
    path = f"/api/accounts/{account.id}/{address}"
    assert (await client.put(path, json={address: new}, headers=headers)).status_code == 204
    await session.refresh(account)
    assert getattr(account, address) == new
    assert to(sent) == {EMAIL, PHONE, new}
    assert old in to(sent)
    await session.refresh(way)
    assert (way.failures, way.disabled_at, way.granted_at) == (0, None, None)
    phone = await session.get_one(Phone, account.id)
    await session.refresh(phone)
    assert (phone.disabled_at is None) == (address == "phone")
    updated = await logged(session, "user_updated")
    assert updated.details == {"changed": [address], "values": {}}
    admin = await logged(session, "authz_admin")
    assert (admin.actor_id, admin.target_id) == (superadmin.id, str(account.id))
    assert (await client.put(path, json={address: new}, headers=headers)).status_code == 204
    other = Account(email="otra@example.com", phone="+56229876543", role=Role.USER, language="es")
    session.add(other)
    await session.flush()
    taken = {address: getattr(other, address)}
    assert (await client.put(path, json=taken, headers=headers)).status_code == 409
    if METHODS & {Method.PASSKEY, Method.PASSWORD}:
        assert (await ask(client, **{address: new})).status_code == 204


async def test_creating_an_account_asks_a_superadmin_freshly_authenticated(
    client: AsyncClient, session: AsyncSession, account: Account, headers: dict[str, str]
) -> None:
    """Another account gets 403, and an old authentication too."""
    path = f"/api/accounts/{uuid4()}"
    sent = {"phone": NEW_PHONE, "role": "user"}
    theirs = await opened(session, account)
    assert (await client.put(path, json=sent, headers=theirs)).status_code == 403
    await age(session, timedelta(minutes=6))
    response = await client.put(path, json=sent, headers=headers)
    assert response.status_code == 403
    assert response.json()["type"] == errors.REAUTHENTICATION_REQUIRED.uri
    found = sa.select(sa.func.count()).where(Account.phone == NEW_PHONE)
    assert await session.scalar(found) == 0


@needs_passkey
@pytest.mark.parametrize("role", [Role.USER, Role.SUPERADMIN])
async def test_superadmin_creates_an_account_its_holder_takes(
    client: AsyncClient,
    session: AsyncSession,
    superadmin: Account,
    headers: dict[str, str],
    sent: list[httpx.Request],
    role: Role,
) -> None:
    """Without an authenticator; the holder recovers it with a passkey.

    The address hears, repeated it answers the same account, and an ID
    or an address of another account is a 409. A superadmin takes the
    code at that address until it signs in.
    """
    account_id = uuid4()
    path = f"/api/accounts/{account_id}"
    created = await client.put(path, json={"phone": NEW_PHONE, "role": role}, headers=headers)
    assert created.status_code == 201
    assert created.json()["id"] == str(account_id)
    assert (created.json()["phone"], created.json()["role"]) == (NEW_PHONE, role)
    target = await session.get_one(Account, account_id)
    assert (target.email, target.role, target.language) == (None, role, "es")
    assert [await count(session, model, target) for model in (Passkey, Password)] == [0, 0]
    assert to(sent) == {NEW_PHONE}
    for action in ("user_created", "authz_admin"):
        row = await logged(session, action)
        assert (row.actor_id, row.target_id) == (superadmin.id, str(account_id))
    again = await client.put(path, json={"phone": NEW_PHONE, "role": role}, headers=headers)
    assert (again.status_code, again.json()) == (200, created.json())
    assert len(sent) == 1
    other = {"phone": PHONE, "role": role}
    assert (await client.put(path, json=other, headers=headers)).status_code == 409
    taken = {"phone": NEW_PHONE, "role": role}
    assert (
        await client.put(f"/api/accounts/{uuid4()}", json=taken, headers=headers)
    ).status_code == 409
    sent.clear()
    assert (await ask(client, phone=NEW_PHONE)).status_code == 204
    proof = {"phone": NEW_PHONE, "code": code_in(sent[0])}
    options = await client.post("/api/auth/recovery/options", json=proof)
    authenticator = Authenticator()
    credential = authenticator.create(options.json()["challenge"])
    response = await client.post(
        "/api/auth/recovery/passkey",
        json={**proof, "passkeyName": "New", "credential": credential},
    )
    assert response.status_code == 204
    login = await client.post("/api/auth/passkey/options")
    signed = authenticator.sign(login.json()["challenge"], target.user_handle)
    assert (await client.post("/api/auth/passkey/token", json=signed)).status_code == 200
    if role == Role.SUPERADMIN:
        assert (await ask(client, phone=NEW_PHONE)).status_code == 403


async def test_superadmin_changes_the_role_of_another_account(
    client: AsyncClient,
    session: AsyncSession,
    account: Account,
    superadmin: Account,
    headers: dict[str, str],
    sent: list[httpx.Request],
) -> None:
    """It rules from the next request, and every address hears.

    The event names both roles, and the same role changes nothing.
    """
    theirs = await opened(session, account)
    path = f"/api/accounts/{account.id}/role"
    assert (await client.get("/api/accounts", headers=theirs)).status_code == 403
    promoted = await client.put(path, json={"role": "superadmin"}, headers=headers)
    assert promoted.status_code == 204
    await session.refresh(account)
    assert account.role == Role.SUPERADMIN
    assert (await client.get("/api/accounts", headers=theirs)).status_code == 200
    assert to(sent) == {EMAIL, PHONE}
    change = await logged(session, "authz_change")
    assert (change.level, change.actor_id) == ("warn", superadmin.id)
    assert change.details == {"from": "user", "to": "superadmin"}
    admin = await logged(session, "authz_admin")
    assert admin.target_id == str(account.id)
    assert (
        await client.put(path, json={"role": "superadmin"}, headers=headers)
    ).status_code == 204
    assert len(sent) == 2
    assert (await client.put(path, json={"role": "user"}, headers=headers)).status_code == 204
    assert (await client.get("/api/accounts", headers=theirs)).status_code == 403


@needs_passkey
async def test_superadmin_recovers_another_superadmin(
    client: AsyncClient,
    session: AsyncSession,
    headers: dict[str, str],
    sent: list[httpx.Request],
) -> None:
    """Only at the address it set, with a passkey with the UV flag.

    Until the superadmin signs in.
    """
    other = await holder(session, Role.SUPERADMIN)
    path = f"/api/accounts/{other.id}/phone"
    assert (await client.put(path, json={"phone": NEW_PHONE}, headers=headers)).status_code == 204
    assert (await ask(client, email=EMAIL)).status_code == 403
    sent.clear()
    assert (await ask(client, phone=NEW_PHONE)).status_code == 204
    proof = {"phone": NEW_PHONE, "code": code_in(sent[0])}
    if Method.PASSWORD in METHODS:
        refused = await client.post(
            "/api/auth/recovery/password", json={**proof, "password": "Staple of a purple ocean"}
        )
        assert refused.status_code == 403
        assert refused.json()["type"] == "about:blank"
    for authenticator, status in ((Authenticator(flags=UP), 403), (Authenticator(), 204)):
        options = await client.post("/api/auth/recovery/options", json=proof)
        credential = authenticator.create(options.json()["challenge"])
        response = await client.post(
            "/api/auth/recovery/passkey",
            json={**proof, "passkeyName": "New", "credential": credential},
        )
        assert response.status_code == status
        if status == 403:
            assert response.json()["type"] == errors.USER_VERIFICATION_REQUIRED.uri
    assert await count(session, Passkey, other) == 1
    login = await client.post("/api/auth/passkey/options")
    signed = authenticator.sign(login.json()["challenge"], other.user_handle)
    assert (await client.post("/api/auth/passkey/token", json=signed)).status_code == 200
    assert (await ask(client, phone=NEW_PHONE)).status_code == 403


async def test_superadmin_closes_the_sessions_of_an_account_or_of_all(
    client: AsyncClient,
    session: AsyncSession,
    account: Account,
    superadmin: Account,
    headers: dict[str, str],
) -> None:
    """One account loses its own, and then everyone but who calls."""
    other = Account(email="otra@example.com", role=Role.USER, language="es")
    session.add(other)
    await session.flush()
    for row in (account, other, superadmin):
        await opened(session, row)
    path = f"/api/accounts/{account.id}/sessions"
    assert (await client.delete(path, headers=headers)).status_code == 204
    assert await count(session, AccountSession, account) == 0
    assert await count(session, AccountSession, other) == 1
    assert (await logged(session, "authz_admin")).target_id == str(account.id)
    assert (await client.delete("/api/accounts/sessions", headers=headers)).status_code == 204
    assert await count(session, AccountSession, other) == 0
    assert await count(session, AccountSession, superadmin) == 1
    assert (await client.get("/api/accounts", headers=headers)).status_code == 200
    closed = await session.scalars(
        sa.select(EventLog.details).where(EventLog.action == "session_logout")
    )
    assert list(closed) == [{"reason": "closed_by_admin"}] * 3
