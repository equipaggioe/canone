"""Sessions: the cookie of the web, and the rotated tokens of an app."""

import base64
import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

import sqlalchemy as sa
from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import SessionFactory
from app.enums import EventLevel, SessionKind, TokenErrorCode
from app.errors import ACCOUNT_DISABLED, AppError, KeptError, TokenRefusal
from app.models.account.account import Account
from app.models.account.account_session import AccountSession
from app.models.event.event_log import EventLog
from app.services import channel, events

COOKIE = "__Host-session"
IDLE = timedelta(days=30)
# The web writes the last use at most this often: once per request
# would load the database without moving the expiry.
TOUCH = timedelta(minutes=15)
ACCESS_LIFETIME = timedelta(minutes=15)
# autenticacion.md: an operation that asks to authenticate again takes
# it within this span.
REAUTHENTICATION = timedelta(minutes=5)


@dataclass(frozen=True)
class Client:
    """Where a request comes from, for its events."""

    ip_address: str | None
    user_agent: str | None

    @property
    def piece(self) -> str:
        """Name the piece that calls: the first product of its agent."""
        return (self.user_agent or "").split(" ", 1)[0].partition("/")[0]


@dataclass(frozen=True)
class Principal:
    """Who calls, and through which session."""

    account: Account
    session: AccountSession


@dataclass(frozen=True)
class Issued:
    """The tokens of an app that opened or refreshed its session."""

    access_token: str
    refresh_token: str
    session_id: UUID


def new_token() -> str:
    """Make 256 random bits."""
    return secrets.token_urlsafe(32)


def digest(token: str) -> bytes:
    """Hash a token: whoever reads the database takes no session."""
    return hashlib.sha256(token.encode()).digest()


def sign(session_id: UUID, secret: str) -> str:
    """Write a refresh token: the session, the secret and their HMAC."""
    payload = f"{session_id.hex}.{secret}"
    mac = hmac.digest(settings.refresh_key.encode(), payload.encode(), "sha256")
    return f"{payload}.{base64.urlsafe_b64encode(mac).rstrip(b'=').decode()}"


def unsign(token: str) -> tuple[UUID, str] | None:
    """Read a refresh token, or none if the server did not sign it."""
    parts = token.split(".")
    if len(parts) != 3:
        return None
    try:
        session_id = UUID(hex=parts[0])
    except ValueError:
        return None
    if not hmac.compare_digest(sign(session_id, parts[1]).encode(), token.encode()):
        return None
    return session_id, parts[1]


def event(action: str, level: EventLevel, row: AccountSession, client: Client) -> EventLog:
    """Build the event of a session."""
    return events.event(
        action,
        level,
        actor_id=row.account_id,
        target_type="account_session",
        target_id=str(row.id),
        ip_address=client.ip_address,
        user_agent=client.user_agent,
    )


def set_cookie(response: Response, token: str) -> None:
    """Send the session cookie, renewing its Max-Age."""
    response.set_cookie(
        COOKIE,
        token,
        max_age=int(IDLE.total_seconds()),
        path="/",
        secure=True,
        httponly=True,
        samesite="strict",
    )


def clear_cookie(response: Response) -> None:
    """Remove the session cookie from the browser."""
    response.delete_cookie(COOKIE, path="/", secure=True, httponly=True, samesite="strict")


def check_enabled(account: Account) -> None:
    """Answer 403 to a disabled account: it opens no session."""
    if account.disabled_at is not None:
        raise AppError(ACCOUNT_DISABLED)


async def open_web(
    session: AsyncSession, account: Account, client: Client, language: str
) -> tuple[str, UUID]:
    """Open a session of the web; return its cookie token and its ID.

    The account keeps the language it signed in with, for its notices.
    """
    check_enabled(account)
    account.language = language
    token = new_token()
    row = AccountSession(
        account_id=account.id,
        kind=SessionKind.WEB,
        token_digest=digest(token),
        authenticated_at=datetime.now(UTC),
        user_agent=client.user_agent,
    )
    session.add(row)
    await session.flush()
    session.add(event("session_created", EventLevel.INFO, row, client))
    return token, row.id


async def open_app(
    session: AsyncSession, account: Account, client: Client, language: str
) -> Issued:
    """Open a session of an app and return its tokens.

    The account keeps the language it signed in with, for its notices.
    """
    check_enabled(account)
    account.language = language
    access, secret = new_token(), new_token()
    now = datetime.now(UTC)
    row = AccountSession(
        account_id=account.id,
        kind=SessionKind.APP,
        token_digest=digest(access),
        token_expires_at=now + ACCESS_LIFETIME,
        secret_digest=digest(secret),
        authenticated_at=now,
        last_used_at=now,
        user_agent=client.user_agent,
    )
    session.add(row)
    await session.flush()
    session.add(event("session_created", EventLevel.INFO, row, client))
    return Issued(access, sign(row.id, secret), row.id)


async def drop(session: AsyncSession, ended: sa.ColumnElement[bool]) -> list[tuple[UUID, UUID]]:
    """Delete the sessions that match, and close their connections.

    Return the ID and the account of each one.
    """
    rows = await session.execute(
        sa.delete(AccountSession)
        .where(ended)
        .returning(AccountSession.id, AccountSession.account_id)
    )
    found = [(session_id, account_id) for session_id, account_id in rows]
    for session_id, account_id in found:
        channel.close(session, account_id, [session_id])
    return found


async def discard(session: AsyncSession, token: str, kind: SessionKind) -> None:
    """Close the session whose token a client brings to a new login."""
    await drop(
        session,
        (AccountSession.token_digest == digest(token)) & (AccountSession.kind == kind),
    )


async def resolve(
    session: AsyncSession, token: str, kind: SessionKind, client: Client
) -> Principal | None:
    """Find the live session of a token, or none."""
    query = (
        sa.select(AccountSession, Account)
        .join(Account, Account.id == AccountSession.account_id)
        .where(AccountSession.token_digest == digest(token), AccountSession.kind == kind)
    )
    found = (await session.execute(query)).one_or_none()
    if found is None:
        return None
    row, account = found
    # A login that raced with the disabling may have left one.
    if account.disabled_at is not None:
        return None
    now = datetime.now(UTC)
    if row.token_expires_at is not None and row.token_expires_at <= now:
        return None
    if now - row.last_used_at > IDLE:
        # The cookie expires with the session: a browser does not bring
        # it later.
        await events.record(event("session_use_after_expire", EventLevel.CRITICAL, row, client))
        return None
    return Principal(account=account, session=row)


def touch(row: AccountSession) -> bool:
    """Write the last use of a web session, at most every TOUCH."""
    now = datetime.now(UTC)
    if now - row.last_used_at <= TOUCH:
        return False
    row.last_used_at = now
    return True


async def refresh(session: AsyncSession, token: str, client: Client) -> Issued:
    """Rotate the secret of an app session, or answer invalid_grant.

    A secret that is neither the current one nor the previous one is a
    reuse: it deletes the session, and the refusal keeps that.
    """
    refused = TokenRefusal(TokenErrorCode.INVALID_GRANT)
    unsigned = unsign(token)
    if unsigned is None:
        raise refused
    session_id, secret = unsigned
    row = await session.get(AccountSession, session_id, with_for_update=True)
    now = datetime.now(UTC)
    if row is None or row.secret_digest is None or now - row.last_used_at > IDLE:
        raise refused
    account = await session.get_one(Account, row.account_id)
    if account.disabled_at is not None:
        raise refused
    presented = digest(secret)
    if hmac.compare_digest(presented, row.secret_digest):
        row.previous_digest = row.secret_digest
    elif row.previous_digest is None or not hmac.compare_digest(presented, row.previous_digest):
        await drop(session, AccountSession.id == row.id)
        session.add(event("authn_token_reuse", EventLevel.CRITICAL, row, client))
        raise KeptError(refused)
    # Presenting the previous secret replaces the current one, and the
    # previous one stays.
    access, new_secret = new_token(), new_token()
    row.token_digest = digest(access)
    row.token_expires_at = now + ACCESS_LIFETIME
    row.secret_digest = digest(new_secret)
    row.last_used_at = now
    session.add(event("session_renewed", EventLevel.INFO, row, client))
    return Issued(access, sign(row.id, new_secret), row.id)


def renew_web(session: AsyncSession, row: AccountSession, client: Client) -> str:
    """Renew a web session that authenticated again; return its token.

    The cookie it brought stops working.
    """
    token = new_token()
    now = datetime.now(UTC)
    row.token_digest = digest(token)
    row.authenticated_at = now
    row.last_used_at = now
    session.add(event("session_renewed", EventLevel.INFO, row, client))
    return token


def renew_app(session: AsyncSession, row: AccountSession, client: Client) -> Issued:
    """Renew an app session that authenticated again: new tokens.

    The access token and both secrets it had stop working.
    """
    access, secret = new_token(), new_token()
    now = datetime.now(UTC)
    row.token_digest = digest(access)
    row.token_expires_at = now + ACCESS_LIFETIME
    row.secret_digest = digest(secret)
    row.previous_digest = None
    row.authenticated_at = now
    row.last_used_at = now
    session.add(event("session_renewed", EventLevel.INFO, row, client))
    return Issued(access, sign(row.id, secret), row.id)


async def close(session: AsyncSession, row: AccountSession, client: Client) -> None:
    """Close a session by deleting its row; the caller commits."""
    await drop(session, AccountSession.id == row.id)
    session.add(event("session_logout", EventLevel.INFO, row, client))


async def close_where(
    session: AsyncSession, closed: sa.ColumnElement[bool], client: Client, reason: str
) -> None:
    """Close the sessions that match, each with its event."""
    for session_id, account_id in await drop(session, closed):
        session.add(
            events.event(
                "session_logout",
                EventLevel.INFO,
                actor_id=account_id,
                target_type="account_session",
                target_id=str(session_id),
                ip_address=client.ip_address,
                user_agent=client.user_agent,
                details={"reason": reason},
            )
        )


async def close_others(session: AsyncSession, row: AccountSession, client: Client) -> None:
    """Close every session of the account but the one that calls."""
    others = (AccountSession.account_id == row.account_id) & (AccountSession.id != row.id)
    await close_where(session, others, client, "closed_by_holder")


async def page(
    session: AsyncSession, account_id: UUID, after: tuple[datetime, UUID] | None, size: int
) -> list[AccountSession]:
    """Return a page of the sessions of an account, newest first."""
    query = sa.select(AccountSession).where(AccountSession.account_id == account_id)
    if after is not None:
        position = sa.tuple_(AccountSession.created_at, AccountSession.id)
        query = query.where(position < sa.tuple_(*after))
    order = (AccountSession.created_at.desc(), AccountSession.id.desc())
    return list(await session.scalars(query.order_by(*order).limit(size)))


async def purge() -> None:
    """Delete the sessions unused for longer than IDLE."""
    cutoff = datetime.now(UTC) - IDLE
    async with SessionFactory.begin() as session:
        expired = await session.execute(
            sa.delete(AccountSession)
            .where(AccountSession.last_used_at < cutoff)
            .returning(AccountSession.id, AccountSession.account_id)
        )
        for session_id, account_id in expired:
            session.add(
                events.event(
                    "session_expired",
                    EventLevel.INFO,
                    actor_id=account_id,
                    target_type="account_session",
                    target_id=str(session_id),
                    details={"reason": "idle"},
                )
            )
