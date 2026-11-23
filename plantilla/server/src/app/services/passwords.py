"""Check a password, with the waits and the limit of its failures."""

import math
import unicodedata
from datetime import UTC, datetime, timedelta
from http import HTTPStatus

import sqlalchemy as sa
from fastapi import HTTPException
from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.enums import EventLevel
from app.errors import AUTHENTICATOR_DISABLED, AppError, KeptError
from app.models.account.account import Account
from app.models.account.password import Password
from app.models.event.event_log import EventLog
from app.schemas.auth import PasswordLogin
from app.services import events
from app.services.sessions import Client

# Argon2id with 64 MiB, 3 passes and 4 lanes.
hasher = PasswordHash.recommended()

WAIT_FROM = 5
FIRST_WAIT = timedelta(seconds=30)
LONGEST_WAIT = timedelta(hours=1)
# 30 seconds doubled 7 times passes the hour.
DOUBLINGS = 7
DISABLE_AT = 100


def wait(failures: int) -> timedelta | None:
    """Return how long the next attempt waits after failures."""
    if failures < WAIT_FROM:
        return None
    return min(FIRST_WAIT * 2 ** min(failures - WAIT_FROM, DOUBLINGS), LONGEST_WAIT)


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


def fail(password: Password, now: datetime) -> None:
    """Count a failure: the waits from the fifth, disabled at 100."""
    password.failures += 1
    delay = wait(password.failures)
    password.retry_at = now + delay if delay else None
    if password.failures >= DISABLE_AT:
        password.disabled_at = now


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
    if password.disabled_at is not None:
        raise AppError(AUTHENTICATOR_DISABLED)
    now = datetime.now(UTC)
    if password.retry_at is not None and now < password.retry_at:
        await events.record(
            event(
                "authn_login_fail_max", EventLevel.WARN, login, client, account, maxlimit=WAIT_FROM
            )
        )
        seconds = math.ceil((password.retry_at - now).total_seconds())
        raise HTTPException(
            HTTPStatus.TOO_MANY_REQUESTS,
            "Too many failed attempts with this password",
            headers={"Retry-After": str(seconds)},
        )
    normalized = unicodedata.normalize("NFC", login.password)
    if not await run_in_threadpool(hasher.verify, normalized, password.hash):
        fail(password, now)
        session.add(event("authn_login_fail", EventLevel.WARN, login, client, account))
        if password.disabled_at is not None:
            session.add(
                event(
                    "authn_login_lock", EventLevel.WARN, login, client, account, reason="failures"
                )
            )
        raise KeptError(HTTPException(HTTPStatus.UNAUTHORIZED))
    retries = password.failures
    password.failures = 0
    password.retry_at = None
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
