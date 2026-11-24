"""Check a password."""

import unicodedata
from datetime import UTC, datetime
from http import HTTPStatus

import sqlalchemy as sa
from fastapi import HTTPException
from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.enums import EventLevel, Role
from app.errors import KeptError
from app.models.account.account import Account
from app.models.account.password import Password
from app.models.event.event_log import EventLog
from app.schemas.auth import PasswordLogin
from app.services import authenticators, events
from app.services.authenticators import WAIT_FROM
from app.services.sessions import Client

# Argon2id with 64 MiB, 3 passes and 4 lanes.
hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a password in NFC."""
    return hasher.hash(unicodedata.normalize("NFC", password))


async def find(session: AsyncSession, login: PasswordLogin) -> tuple[Account, Password] | None:
    """Find the account of the login and lock its password.

    An admin signs in only with a passkey: its password is ignored.
    """
    identifier = Account.email == login.email if login.email else Account.phone == login.phone
    query = (
        sa.select(Account, Password)
        .join(Password, Password.account_id == Account.id)
        .where(identifier, Account.role != Role.ADMIN)
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
    failure and its event stay.
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
