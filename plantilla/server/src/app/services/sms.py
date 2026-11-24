"""Sign in with the code of an SMS: the phone is its authenticator."""

from datetime import UTC, datetime
from http import HTTPStatus

import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import methods
from app.enums import EventLevel, Method, Role
from app.errors import INVALID_CODE, AppError, KeptError
from app.models.account.account import Account
from app.models.account.phone import Phone
from app.models.event.event_log import EventLog
from app.services import authenticators, codes, events, limits, notices, sessions
from app.services.authenticators import WAIT_FROM
from app.services.sessions import Client

PURPOSE = "sms"


def refuse_superadmin(account: Account) -> None:
    """Answer 403 to a superadmin, who signs in only with a passkey."""
    if account.role == Role.SUPERADMIN and Method.PASSKEY in methods.METHODS:
        raise HTTPException(HTTPStatus.FORBIDDEN, "A superadmin signs in only with a passkey")


def event(
    action: str,
    level: EventLevel,
    phone: str,
    client: Client,
    account: Account | None = None,
    **details: object,
) -> EventLog:
    """Build the event of a login with the code of an SMS."""
    return events.event(
        action,
        level,
        actor_id=account.id if account else None,
        actor_label=phone,
        target_type="phone",
        target_id=str(account.id) if account else None,
        ip_address=client.ip_address,
        user_agent=client.user_agent,
        details=details,
    )


async def find(session: AsyncSession, phone: str) -> tuple[Account, Phone] | None:
    """Find the account of a phone and lock its failures."""
    query = (
        sa.select(Account, Phone)
        .join(Phone, Phone.account_id == Account.id)
        .where(Account.phone == phone)
        .with_for_update(of=Phone)
    )
    return (await session.execute(query)).one_or_none()


async def send_code(
    session: AsyncSession, phone: str, client: Client, language: str, host: str
) -> None:
    """Send the code to sign in, or answer 404 to an unknown phone.

    A disabled phone, one before its wait, or the phone of a superadmin
    that signs in only with a passkey gets no SMS.
    """
    await codes.check_open(client)
    found = await find(session, phone)
    if found is None:
        raise await codes.unknown(client)
    account, row = found
    sessions.check_enabled(account)
    refuse_superadmin(account)
    early = event(
        "authn_login_fail_max", EventLevel.WARN, phone, client, account, maxlimit=WAIT_FROM
    )
    await authenticators.admit(row, datetime.now(UTC), early)
    await limits.take(client, *codes.sms_rules(phone, client))
    code = await codes.issue(PURPOSE, phone)
    codes.send_sms(session, phone, codes.sms_text(code, language, host, client.piece))


async def check(session: AsyncSession, phone: str, code: str, client: Client) -> Account:
    """Return the account of a right code, or answer 400 invalid-code.

    A wrong code counts against the phone, and stays with its event, as
    in any account. An unknown phone gets the same answer.
    """
    found = await find(session, phone)
    if found is None:
        session.add(event("authn_login_fail", EventLevel.WARN, phone, client))
        raise KeptError(AppError(INVALID_CODE))
    account, row = found
    sessions.check_enabled(account)
    now = datetime.now(UTC)
    early = event(
        "authn_login_fail_max", EventLevel.WARN, phone, client, account, maxlimit=WAIT_FROM
    )
    await authenticators.admit(row, now, early)
    if not await codes.take(PURPOSE, phone, code):
        disabled = authenticators.fail(row, now)
        session.add(event("authn_login_fail", EventLevel.WARN, phone, client, account))
        if disabled:
            session.add(
                event(
                    "authn_login_lock", EventLevel.WARN, phone, client, account, reason="failures"
                )
            )
        raise KeptError(AppError(INVALID_CODE))
    refuse_superadmin(account)
    retries = authenticators.succeed(row)
    if retries:
        session.add(
            event(
                "authn_login_successafterfail",
                EventLevel.INFO,
                phone,
                client,
                account,
                retries=retries,
            )
        )
    else:
        session.add(event("authn_login_success", EventLevel.INFO, phone, client, account))
    return account


def bind(session: AsyncSession, account: Account) -> None:
    """Make the phone of a new account its authenticator."""
    session.add(Phone(account_id=account.id))


async def rebind(session: AsyncSession, account: Account) -> None:
    """Make a new phone of the account its authenticator.

    Another number is another authenticator: it waits nothing, and
    starts enabled.
    """
    row = await session.get(Phone, account.id, with_for_update=True)
    if row is None:
        bind(session, account)
        return
    row.changed_at = datetime.now(UTC)
    row.failures, row.retry_at, row.disabled_at = 0, None, None


async def enable(session: AsyncSession, account: Account, client: Client) -> None:
    """Enable the disabled phone of the account again.

    It binds the phone again: its failures go to zero, and every address
    hears. A phone that is not disabled stays as it is.
    """
    if account.phone is None:
        raise HTTPException(HTTPStatus.CONFLICT, "The account has no phone")
    row = await session.get_one(Phone, account.id, with_for_update=True)
    if row.disabled_at is None:
        return
    authenticators.enable(row)
    row.changed_at = datetime.now(UTC)
    session.add(
        events.event(
            "sensitive_update",
            EventLevel.INFO,
            actor_id=account.id,
            target_type="phone",
            target_id=str(account.id),
            ip_address=client.ip_address,
            user_agent=client.user_agent,
        )
    )
    notices.notify(session, account, notices.Notice.PHONE_ENABLED)
