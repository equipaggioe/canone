"""Check a password, and add or change one."""

import unicodedata
from datetime import UTC, datetime
from http import HTTPStatus
from pathlib import Path

import sqlalchemy as sa
from fastapi import HTTPException
from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app import methods
from app.enums import EventLevel, Method, Role
from app.errors import PASSWORD_BLOCKED, AppError, KeptError
from app.models.account.account import Account
from app.models.account.account_session import AccountSession
from app.models.account.password import Password
from app.models.event.event_log import EventLog
from app.schemas.auth import PasswordLogin
from app.services import authenticators, events, notices
from app.services.authenticators import WAIT_FROM
from app.services.sessions import Client, Principal

# Argon2id with 64 MiB, 3 passes and 4 lanes.
hasher = PasswordHash.recommended()


def words(name: str) -> frozenset[str]:
    """Read a list of the app, one password a line, in casefold."""
    lines = (Path(__file__).parent.parent / name).read_text(encoding="utf-8").splitlines()
    return frozenset(unicodedata.normalize("NFC", line).casefold() for line in lines if line)


# It comes from the list of the NCSC, by scripts/bloqueo.py of Canone.
BLOCKLIST = words("blocklist.txt")


def blocked(password: str) -> bool:
    """Tell whether the whole password is on the blocklist, any case."""
    return unicodedata.normalize("NFC", password).casefold() in BLOCKLIST


def hash_password(password: str) -> str:
    """Hash a password in NFC."""
    return hasher.hash(unicodedata.normalize("NFC", password))


async def find(session: AsyncSession, login: PasswordLogin) -> tuple[Account, Password] | None:
    """Find the account of the login and lock its password."""
    identifier = Account.email == login.email if login.email else Account.phone == login.phone
    query = (
        sa.select(Account, Password)
        .join(Password, Password.account_id == Account.id)
        .where(identifier)
        .with_for_update(of=Password)
    )
    return (await session.execute(query)).one_or_none()


def event(
    action: str,
    level: EventLevel,
    login: PasswordLogin,
    client: Client,
    account: Account | None = None,
    **details: object,
) -> EventLog:
    """Build the event of a login with a password."""
    return events.event(
        action,
        level,
        actor_id=account.id if account else None,
        actor_label=login.email or login.phone,
        target_type="password",
        ip_address=client.ip_address,
        user_agent=client.user_agent,
        details=details,
    )


async def check(session: AsyncSession, login: PasswordLogin, client: Client) -> Account:
    """Return the account of a right password, or answer 401.

    A wrong password, or an unknown account, raises a KeptError: the
    failure and its event stay. Where the product offers the passkey,
    an admin with the right password gets 403: only whoever knows the
    password sees it.
    """
    found = await find(session, login)
    if found is None:
        session.add(event("authn_login_fail", EventLevel.WARN, login, client))
        raise KeptError(HTTPException(HTTPStatus.UNAUTHORIZED))
    account, password = found
    now = datetime.now(UTC)
    early = event(
        "authn_login_fail_max", EventLevel.WARN, login, client, account, maxlimit=WAIT_FROM
    )
    await authenticators.admit(password, now, early)
    normalized = unicodedata.normalize("NFC", login.password)
    if not await run_in_threadpool(hasher.verify, normalized, password.hash):
        disabled = authenticators.fail(password, now)
        session.add(event("authn_login_fail", EventLevel.WARN, login, client, account))
        if disabled:
            session.add(
                event(
                    "authn_login_lock", EventLevel.WARN, login, client, account, reason="failures"
                )
            )
        raise KeptError(HTTPException(HTTPStatus.UNAUTHORIZED))
    if account.role == Role.ADMIN and Method.PASSKEY in methods.METHODS:
        raise HTTPException(HTTPStatus.FORBIDDEN, "An admin signs in only with a passkey")
    retries = authenticators.succeed(password)
    if retries:
        session.add(
            event(
                "authn_login_successafterfail",
                EventLevel.INFO,
                login,
                client,
                account,
                retries=retries,
            )
        )
    else:
        session.add(event("authn_login_success", EventLevel.INFO, login, client, account))
    return account


def check_new(session: AsyncSession, account: Account, password: str, client: Client) -> None:
    """Refuse a password on the blocklist, and log the refusal."""
    if not blocked(password):
        return
    session.add(
        events.event(
            "authn_password_change_fail",
            EventLevel.WARN,
            actor_id=account.id,
            target_type="password",
            target_id=str(account.id),
            ip_address=client.ip_address,
            user_agent=client.user_agent,
            details={"reason": "blocklist"},
        )
    )
    raise KeptError(AppError(PASSWORD_BLOCKED))


def changed(session: AsyncSession, account: Account, client: Client) -> None:
    """Log that the password of an account was added or changed."""
    session.add(
        events.event(
            "authn_password_change",
            EventLevel.INFO,
            actor_id=account.id,
            target_type="password",
            target_id=str(account.id),
            ip_address=client.ip_address,
            user_agent=client.user_agent,
        )
    )


async def close_others(session: AsyncSession, principal: Principal, client: Client) -> None:
    """Close every other session of the account."""
    closed = await session.execute(
        sa.delete(AccountSession)
        .where(
            AccountSession.account_id == principal.account.id,
            AccountSession.id != principal.session.id,
        )
        .returning(AccountSession.id)
    )
    for (session_id,) in closed:
        session.add(
            events.event(
                "session_expired",
                EventLevel.INFO,
                actor_id=principal.account.id,
                target_type="account_session",
                target_id=str(session_id),
                ip_address=client.ip_address,
                user_agent=client.user_agent,
                details={"reason": "password_change"},
            )
        )


async def put(session: AsyncSession, principal: Principal, password: str, client: Client) -> bool:
    """Add or change the password of the account; tell if it is new.

    A change is another secret: it waits nothing and closes the other
    sessions. Where the product offers the passkey, an admin signs in
    only with it.
    """
    account = principal.account
    if account.role == Role.ADMIN and Method.PASSKEY in methods.METHODS:
        raise HTTPException(HTTPStatus.FORBIDDEN, "An admin signs in only with a passkey")
    check_new(session, account, password, client)
    digest = await run_in_threadpool(hash_password, password)
    now = datetime.now(UTC)
    row = await session.get(Password, account.id, with_for_update=True)
    if row is None:
        session.add(Password(account_id=account.id, hash=digest, created_at=now, changed_at=now))
    else:
        row.hash, row.changed_at = digest, now
        row.failures, row.retry_at, row.disabled_at = 0, None, None
        await close_others(session, principal, client)
    changed(session, account, client)
    notice = notices.Notice.PASSWORD_ADDED if row is None else notices.Notice.PASSWORD_CHANGED
    notices.notify(session, account, notice)
    return row is None
