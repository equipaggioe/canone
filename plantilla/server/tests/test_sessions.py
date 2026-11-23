"""Signing in with a password, the sessions and their tokens."""

import base64
import hashlib
import hmac
import unicodedata
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from http.cookies import SimpleCookie
from uuid import UUID, uuid4

import pytest
import sqlalchemy as sa
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession

from app import errors, tasks
from app.config import settings
from app.dependencies import PrincipalDep
from app.models.account.account import Account
from app.models.account.account_session import AccountSession
from app.models.account.password import Password
from app.models.event.event_log import EventLog
from app.services import authenticators, events, passwords, sessions

PASSWORD = "Correct horse battery"
EMAIL = "ana@example.com"
PHONE = "+56912345678"
ORIGIN = {"Origin": "https://test"}

probe = FastAPI()
errors.install(probe)


@probe.get("/whoami")
async def whoami(principal: PrincipalDep) -> dict[str, str]:
    """Answer the account of the session that calls."""
    return {"account": str(principal.account.id)}


@pytest.fixture
async def account(session: AsyncSession) -> Account:
    """Create an account with an email, a phone and a password."""
    row = Account(email=EMAIL, phone=PHONE)
    session.add(row)
    await session.flush()
    session.add(Password(account_id=row.id, hash=passwords.hash_password(PASSWORD)))
    await session.flush()
    return row


@pytest.fixture
def recorded(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Collect the events written in their own transaction.

    In a test that transaction is a savepoint of the request, and a
    request that fails would undo it.
    """
    found: list[str] = []

    async def record(row: EventLog) -> None:
        """Keep the action of the event."""
        found.append(row.action)

    monkeypatch.setattr(events, "record", record)
    return found


@pytest.fixture
async def guarded(database: AsyncConnection) -> AsyncIterator[AsyncClient]:
    """Call a route that only a signed-in account reaches."""
    async with AsyncClient(transport=ASGITransport(app=probe), base_url="http://test") as client:
        yield client


def session_cookie(response: Response) -> str:
    """Return the value of the session cookie a response sets."""
    return SimpleCookie(response.headers["set-cookie"])[sessions.COOKIE].value


def with_cookie(token: str) -> dict[str, str]:
    """Send a session cookie: the client does not keep a Secure one."""
    return {"Cookie": f"{sessions.COOKIE}={token}"}


async def sign_in_web(client: AsyncClient) -> str:
    """Sign in with the cookie and return its token."""
    response = await client.post(
        "/api/auth/password/cookie", json={"email": EMAIL, "password": PASSWORD}
    )
    assert response.status_code == 204
    return session_cookie(response)


async def sign_in_app(client: AsyncClient) -> dict[str, str]:
    """Sign in an app and return its token response."""
    response = await client.post(
        "/api/auth/password/token", json={"email": EMAIL, "password": PASSWORD}
    )
    assert response.status_code == 200
    body: dict[str, str] = response.json()
    return body


async def refresh(client: AsyncClient, token: str) -> Response:
    """Present a refresh token to the token endpoint."""
    return await client.post(
        "/api/auth/token", data={"grant_type": "refresh_token", "refresh_token": token}
    )


async def actions(session: AsyncSession) -> list[str]:
    """Return the actions of the events, in order."""
    return list(await session.scalars(sa.select(EventLog.action).order_by(EventLog.id)))


async def age(session: AsyncSession, last_used: timedelta) -> None:
    """Move the last use of every session to the past."""
    moment = datetime.now(UTC) - last_used
    await session.execute(sa.update(AccountSession).values(last_used_at=moment))


async def test_cookie_is_host_secure_httponly_strict(
    client: AsyncClient, account: Account
) -> None:
    """The cookie is __Host-session, Secure, HttpOnly, Strict, Path=/.

    It lasts the 30 days without use of the session.
    """
    response = await client.post(
        "/api/auth/password/cookie", json={"email": EMAIL, "password": PASSWORD}
    )
    morsel = SimpleCookie(response.headers["set-cookie"])["__Host-session"]
    assert morsel["secure"] is True
    assert morsel["httponly"] is True
    assert morsel["samesite"] == "strict"
    assert morsel["path"] == "/"
    assert morsel["domain"] == ""
    assert morsel["max-age"] == str(30 * 24 * 3600)


async def test_web_token_is_random_and_hashed(
    client: AsyncClient, session: AsyncSession, account: Account
) -> None:
    """The cookie carries 256 random bits, and the row their SHA-256."""
    first, second = await sign_in_web(client), await sign_in_web(client)
    assert first != second
    assert len(base64.urlsafe_b64decode(first + "=")) == 32
    digests = set(await session.scalars(sa.select(AccountSession.token_digest)))
    assert hashlib.sha256(first.encode()).digest() in digests


async def test_cookie_without_session_is_401_without_challenge(
    client: AsyncClient, guarded: AsyncClient, account: Account
) -> None:
    """The cookie reaches the account; an unknown one is a bare 401."""
    token = await sign_in_web(client)
    assert (await guarded.get("/whoami", headers=with_cookie(token))).json() == {
        "account": str(account.id)
    }
    none: dict[str, str] = {}
    for headers in (with_cookie("unknown"), none):
        response = await guarded.get("/whoami", headers=headers)
        assert response.status_code == 401
        assert "www-authenticate" not in response.headers


async def test_web_writes_last_use_every_15_minutes(
    client: AsyncClient, guarded: AsyncClient, session: AsyncSession, account: Account
) -> None:
    """The last use and the Max-Age move only after 15 minutes."""
    token = await sign_in_web(client)
    await age(session, timedelta(minutes=14))
    assert "set-cookie" not in (await guarded.get("/whoami", headers=with_cookie(token))).headers
    await age(session, timedelta(minutes=16))
    response = await guarded.get("/whoami", headers=with_cookie(token))
    assert session_cookie(response) == token
    last_used = await session.scalar(sa.select(AccountSession.last_used_at))
    assert last_used is not None
    assert datetime.now(UTC) - last_used < timedelta(minutes=1)


async def test_session_expires_after_30_days_without_use(
    client: AsyncClient,
    guarded: AsyncClient,
    session: AsyncSession,
    account: Account,
    recorded: list[str],
) -> None:
    """A cookie and a refresh unused for 30 days no longer sign in."""
    token = await sign_in_web(client)
    app = await sign_in_app(client)
    await age(session, timedelta(days=30, minutes=1))
    assert (await guarded.get("/whoami", headers=with_cookie(token))).status_code == 401
    assert (await refresh(client, app["refresh_token"])).json() == {"error": "invalid_grant"}
    assert recorded == ["session_use_after_expire"]


async def test_purge_deletes_sessions_unused_for_30_days(
    client: AsyncClient, session: AsyncSession, account: Account
) -> None:
    """The purge deletes the sessions past 30 days without use."""
    await sign_in_web(client)
    await age(session, timedelta(days=30, minutes=1))
    kept = await sign_in_web(client)
    await sessions.purge()
    digests = (await session.scalars(sa.select(AccountSession.token_digest))).all()
    assert digests == [hashlib.sha256(kept.encode()).digest()]
    assert "session_expired" in await actions(session)


async def test_purge_task_deletes_expired_sessions(
    client: AsyncClient, session: AsyncSession, account: Account, owner: None
) -> None:
    """The daily purge also deletes the expired sessions."""
    await sign_in_web(client)
    await age(session, timedelta(days=30, minutes=1))
    await tasks.purge()
    assert (await session.scalars(sa.select(AccountSession.id))).all() == []


@pytest.mark.parametrize("origin", [{}, {"Origin": "https://evil.example"}, {"Origin": "null"}])
async def test_unsafe_request_with_cookie_needs_the_origin(
    client: AsyncClient, session: AsyncSession, account: Account, origin: dict[str, str]
) -> None:
    """A POST with the cookie and without the server's Origin is a 403.

    A GET passes, and so does a POST with the Origin of the server.
    """
    token = await sign_in_web(client)
    response = await client.post("/api/auth/logout", headers={**with_cookie(token), **origin})
    assert response.status_code == 403
    assert "malicious_csrf" in await actions(session)
    assert (await client.get("/api/health", headers=with_cookie(token))).status_code == 204
    headers = {**with_cookie(token), **ORIGIN}
    assert (await client.post("/api/auth/logout", headers=headers)).status_code == 204


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


async def test_refresh_token_is_the_session_and_a_secret(
    client: AsyncClient, session: AsyncSession, account: Account
) -> None:
    """The refresh token: the session id and 256 bits, with an HMAC."""
    session_id, secret, mac = (await sign_in_app(client))["refresh_token"].split(".")
    assert UUID(hex=session_id) == await session.scalar(sa.select(AccountSession.id))
    assert len(base64.urlsafe_b64decode(secret + "=")) == 32
    expected = hmac.digest(
        settings.refresh_key.encode(), f"{session_id}.{secret}".encode(), "sha256"
    )
    assert base64.urlsafe_b64decode(mac + "=") == expected


async def test_access_token_lasts_15_minutes(
    client: AsyncClient, guarded: AsyncClient, session: AsyncSession, account: Account
) -> None:
    """An opaque token of 256 bits that lasts 15 minutes.

    The row keeps its SHA-256. Expired or unknown, it is a Bearer 401.
    """
    app = await sign_in_app(client)
    assert len(base64.urlsafe_b64decode(app["access_token"] + "=")) == 32
    stored = await session.scalar(sa.select(AccountSession.token_digest))
    assert stored == hashlib.sha256(app["access_token"].encode()).digest()
    bearer = {"Authorization": f"Bearer {app['access_token']}"}
    assert (await guarded.get("/whoami", headers=bearer)).status_code == 200
    expires_at = await session.scalar(sa.select(AccountSession.token_expires_at))
    assert expires_at is not None
    assert abs(expires_at - datetime.now(UTC) - timedelta(minutes=15)) < timedelta(minutes=1)
    await session.execute(
        sa.update(AccountSession).values(token_expires_at=datetime.now(UTC) - timedelta(seconds=1))
    )
    for headers in (bearer, {"Authorization": "Bearer unknown"}):
        response = await guarded.get("/whoami", headers=headers)
        assert response.status_code == 401
        assert response.headers["www-authenticate"] == "Bearer"


async def test_tokens_are_not_interchangeable(
    client: AsyncClient, guarded: AsyncClient, account: Account
) -> None:
    """The access token is no cookie, and the cookie no access token."""
    app = await sign_in_app(client)
    token = await sign_in_web(client)
    response = await guarded.get("/whoami", headers=with_cookie(app["access_token"]))
    assert response.status_code == 401
    response = await guarded.get("/whoami", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


async def test_refresh_rotates_the_secret(
    client: AsyncClient, guarded: AsyncClient, session: AsyncSession, account: Account
) -> None:
    """A refresh answers new tokens, and the old access token dies.

    It writes the last use of the session.
    """
    app = await sign_in_app(client)
    await age(session, timedelta(days=1))
    response = await refresh(client, app["refresh_token"])
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["pragma"] == "no-cache"
    renewed = response.json()
    assert renewed["refresh_token"] != app["refresh_token"]
    assert renewed["access_token"] != app["access_token"]
    old = {"Authorization": f"Bearer {app['access_token']}"}
    assert (await guarded.get("/whoami", headers=old)).status_code == 401
    new = {"Authorization": f"Bearer {renewed['access_token']}"}
    assert (await guarded.get("/whoami", headers=new)).status_code == 200
    last_used = await session.scalar(sa.select(AccountSession.last_used_at))
    assert last_used is not None
    assert datetime.now(UTC) - last_used < timedelta(minutes=1)
    assert (await refresh(client, renewed["refresh_token"])).status_code == 200


async def test_previous_secret_replaces_the_current_one(
    client: AsyncClient, session: AsyncSession, account: Account
) -> None:
    """The previous secret works while the current is unused.

    It replaces the current one and stays the previous: the current one
    it replaced is then a reuse.
    """
    first = (await sign_in_app(client))["refresh_token"]
    second = (await refresh(client, first)).json()["refresh_token"]
    third = await refresh(client, first)
    assert third.status_code == 200
    assert (await refresh(client, second)).json() == {"error": "invalid_grant"}
    assert (await session.scalars(sa.select(AccountSession.id))).all() == []
    assert "authn_token_reuse" in await actions(session)


async def test_reused_secret_deletes_the_session(
    client: AsyncClient, session: AsyncSession, account: Account
) -> None:
    """A secret neither current nor previous is a reuse."""
    first = (await sign_in_app(client))["refresh_token"]
    second = (await refresh(client, first)).json()["refresh_token"]
    third = (await refresh(client, second)).json()["refresh_token"]
    assert (await refresh(client, first)).json() == {"error": "invalid_grant"}
    assert (await session.scalars(sa.select(AccountSession.id))).all() == []
    assert (await refresh(client, third)).json() == {"error": "invalid_grant"}
    assert await actions(session) == [
        "authn_login_success",
        "session_created",
        "session_renewed",
        "session_renewed",
        "authn_token_reuse",
    ]


async def test_forged_refresh_token_is_invalid_grant_without_notice(
    client: AsyncClient, session: AsyncSession, account: Account
) -> None:
    """A bad signature or no session: invalid_grant, and no reuse."""
    token = (await sign_in_app(client))["refresh_token"]
    session_id, secret, _ = token.split(".")
    forged = [f"{session_id}.{secret}.AAAA", f"{session_id}.other.{token.split('.')[2]}"]
    forged.append(sessions.sign(uuid4(), secret))
    for presented in forged:
        assert (await refresh(client, presented)).json() == {"error": "invalid_grant"}
    assert len((await session.scalars(sa.select(AccountSession.id))).all()) == 1
    assert "authn_token_reuse" not in await actions(session)


@pytest.mark.parametrize(
    ("body", "error"),
    [
        ("grant_type=refresh_token&refresh_token=a&refresh_token=b", "invalid_request"),
        ("grant_type=refresh_token&grant_type=refresh_token&refresh_token=a", "invalid_request"),
        ("refresh_token=a", "invalid_request"),
        ("grant_type=&refresh_token=a", "invalid_request"),
        ("grant_type=refresh_token", "invalid_request"),
        ("grant_type=refresh_token&refresh_token=", "invalid_request"),
        ("grant_type=refresh_token&refresh_token=a&scope=all", "invalid_scope"),
        ("grant_type=password&refresh_token=a", "unsupported_grant_type"),
        ("grant_type=refresh_token&refresh_token=a&unknown=1", "invalid_grant"),
        ("grant_type=refresh_token&refresh_token=a&scope=", "invalid_grant"),
    ],
)
async def test_token_endpoint_parameters(client: AsyncClient, body: str, error: str) -> None:
    """A repeated or missing parameter is invalid_request, never a 422.

    A parameter without a value is absent, and an unknown one ignored.
    """
    response = await client.post(
        "/api/auth/token",
        content=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 400
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {"error": error}


async def test_token_endpoint_takes_only_a_form_post(client: AsyncClient) -> None:
    """Another media type is invalid_request; a GET, no endpoint."""
    response = await client.post(
        "/api/auth/token",
        content="grant_type=refresh_token&refresh_token=a",
        headers={"Content-Type": "application/json"},
    )
    assert response.json() == {"error": "invalid_request"}
    assert (await client.get("/api/auth/token")).status_code == 405


async def test_logout_deletes_the_session(
    client: AsyncClient, guarded: AsyncClient, session: AsyncSession, account: Account
) -> None:
    """Signing out deletes the row, and the web loses its cookie."""
    token = await sign_in_web(client)
    response = await client.post("/api/auth/logout", headers={**with_cookie(token), **ORIGIN})
    assert response.status_code == 204
    assert SimpleCookie(response.headers["set-cookie"])[sessions.COOKIE]["max-age"] == "0"
    app = await sign_in_app(client)
    bearer = {"Authorization": f"Bearer {app['access_token']}"}
    assert (await client.post("/api/auth/logout", headers=bearer)).status_code == 204
    assert (await session.scalars(sa.select(AccountSession.id))).all() == []
    assert (await guarded.get("/whoami", headers=bearer)).status_code == 401
    assert (await refresh(client, app["refresh_token"])).json() == {"error": "invalid_grant"}


async def test_sign_in_discards_the_tokens_it_brings(
    client: AsyncClient, guarded: AsyncClient, account: Account
) -> None:
    """A new login kills the cookie or the access token it brings."""
    old = await sign_in_web(client)
    response = await client.post(
        "/api/auth/password/cookie",
        json={"email": EMAIL, "password": PASSWORD},
        headers={**with_cookie(old), **ORIGIN},
    )
    assert (await guarded.get("/whoami", headers=with_cookie(old))).status_code == 401
    assert (await guarded.get("/whoami", headers=with_cookie(session_cookie(response)))).is_success
    app = await sign_in_app(client)
    bearer = {"Authorization": f"Bearer {app['access_token']}"}
    response = await client.post(
        "/api/auth/password/token", json={"email": EMAIL, "password": PASSWORD}, headers=bearer
    )
    assert response.status_code == 200
    assert (await guarded.get("/whoami", headers=bearer)).status_code == 401


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


def test_wait_doubles_from_the_fifth_failure_up_to_an_hour() -> None:
    """No wait before the fifth failure; 30 s doubling up to an hour."""
    assert [authenticators.wait(failures) for failures in (1, 4)] == [None, None]
    assert authenticators.wait(5) == timedelta(seconds=30)
    assert authenticators.wait(6) == timedelta(seconds=60)
    assert authenticators.wait(11) == timedelta(seconds=1920)
    assert authenticators.wait(12) == timedelta(hours=1)
    assert authenticators.wait(99) == timedelta(hours=1)


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
