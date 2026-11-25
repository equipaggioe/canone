"""The account of the session: its authenticators, failures and end."""

from datetime import UTC, datetime
from http import HTTPStatus
from uuid import UUID

import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from webauthn.helpers import base64url_to_bytes

from app.enums import Address, Credential, EventLevel
from app.errors import INVALID_CODE, AppError
from app.models.account.account import Account
from app.models.account.account_session import AccountSession
from app.models.account.passkey import Passkey
from app.models.account.password import Password
from app.models.account.phone import Phone
from app.models.event.event_log import EventLog
from app.schemas.account import AccountView, FailureView, PasskeyLink, PasswordView, PhoneView
from app.services import (
    attestation,
    authenticators,
    codes,
    events,
    limits,
    notices,
    recovery,
    sessions,
    sms,
)
from app.services.sessions import Client

PURPOSE = "change"
# The events the holder sees as failed attempts.
FAILURES = ("authn_login_fail", "authn_token_reuse")
# The credential of a failure, by the target of its event.
TARGETS = {
    "password": Credential.PASSWORD,
    "passkey": Credential.PASSKEY,
    "phone": Credential.SMS_CODE,
    "account_session": Credential.REFRESH_TOKEN,
}
# The credential of a failure of the recovery, by its way.
WAYS = {
    "email": Credential.EMAIL_RECOVERY,
    "phone": Credential.PHONE_RECOVERY,
    "saved_code": Credential.SAVED_CODE,
}


def event(
    action: str,
    account: Account,
    client: Client,
    target: tuple[str, str],
    details: dict[str, object] | None = None,
) -> EventLog:
    """Build the event of a change of the account, with its origin."""
    return events.event(
        action,
        EventLevel.INFO,
        actor_id=account.id,
        target_type=target[0],
        target_id=target[1],
        ip_address=client.ip_address,
        user_agent=client.user_agent,
        details=details,
    )


async def view(session: AsyncSession, account: Account) -> AccountView:
    """Show the account, with its password and its phone."""
    phone = None
    if account.phone is not None:
        row = await session.get_one(Phone, account.id)
        phone = PhoneView(
            number=account.phone, changed_at=row.changed_at, disabled_at=row.disabled_at
        )
    password = await session.get(Password, account.id)
    return AccountView(
        id=account.id,
        email=account.email,
        phone=phone,
        role=account.role,
        created_at=account.created_at,
        password=PasswordView.model_validate(password) if password else None,
    )


def failure(row: EventLog) -> FailureView:
    """Show a failed attempt by what it presented."""
    if row.target_type == "recovery":
        credential = WAYS[row.details["way"]]
    else:
        credential = TARGETS[str(row.target_type)]
    passkey_id = (
        UUID(row.target_id) if credential == Credential.PASSKEY and row.target_id else None
    )
    return FailureView.model_validate(
        {
            "occurred_at": row.occurred_at,
            "credential": credential,
            "passkey_id": passkey_id,
            "ip_address": row.ip_address,
            "user_agent": row.user_agent,
        }
    )


async def failures(
    session: AsyncSession, account: Account, after: tuple[datetime, int] | None, size: int
) -> list[EventLog]:
    """Return a page of the failed attempts newest first."""
    query = sa.select(EventLog).where(
        EventLog.actor_id == account.id, EventLog.action.in_(FAILURES)
    )
    if after is not None:
        query = query.where(sa.tuple_(EventLog.occurred_at, EventLog.id) < sa.tuple_(*after))
    order = (EventLog.occurred_at.desc(), EventLog.id.desc())
    return list(await session.scalars(query.order_by(*order).limit(size)))


async def passkeys(
    session: AsyncSession, account: Account, after: tuple[datetime, UUID] | None, size: int
) -> list[Passkey]:
    """Return a page of the passkeys of the account, oldest first."""
    query = sa.select(Passkey).where(Passkey.account_id == account.id)
    if after is not None:
        query = query.where(sa.tuple_(Passkey.created_at, Passkey.id) > sa.tuple_(*after))
    query = query.order_by(Passkey.created_at, Passkey.id).limit(size)
    return list(await session.scalars(query))


async def all_passkeys(session: AsyncSession, account: Account) -> list[Passkey]:
    """Return every passkey of the account, for a ceremony."""
    query = sa.select(Passkey).where(Passkey.account_id == account.id).order_by(Passkey.id)
    return list(await session.scalars(query))


async def link(
    session: AsyncSession, account: Account, passkey_id: UUID, body: PasskeyLink, client: Client
) -> tuple[Passkey, bool]:
    """Link a passkey by the ID the client made; tell if it is new.

    A PUT repeated with the same credential finds the same passkey.
    """
    existing = await session.get(Passkey, passkey_id)
    if existing is not None:
        same = base64url_to_bytes(body.credential.raw_id) == existing.credential_id
        if existing.account_id != account.id or not same:
            raise HTTPException(HTTPStatus.CONFLICT, "The ID is of another passkey")
        return existing, False
    created = await attestation.create(session, body.credential, client)
    if created.user_handle != account.user_handle:
        raise HTTPException(HTTPStatus.BAD_REQUEST, "The options were of another account")
    row = attestation.keep(session, account, created, body.name, passkey_id, client)
    notices.notify(session, account, notices.Notice.PASSKEY_LINKED, name=body.name)
    return row, True


async def unlink(
    session: AsyncSession, account: Account, passkey_id: UUID, client: Client
) -> None:
    """Delete a passkey of the account, or answer 404."""
    row = await session.get(Passkey, passkey_id)
    if row is None or row.account_id != account.id:
        raise HTTPException(HTTPStatus.NOT_FOUND)
    await session.delete(row)
    session.add(event("sensitive_delete", account, client, ("passkey", str(row.id))))
    notices.notify(session, account, notices.Notice.PASSKEY_DELETED, name=row.name)


async def enable(
    session: AsyncSession, account: Account, passkey_id: UUID, client: Client
) -> None:
    """Enable a disabled passkey of the account again, or answer 404.

    It binds the passkey again: its failures go to zero, and every
    address hears. One that is not disabled stays as it is.
    """
    row = await session.get(Passkey, passkey_id, with_for_update=True)
    if row is None or row.account_id != account.id:
        raise HTTPException(HTTPStatus.NOT_FOUND)
    if row.disabled_at is None:
        return
    authenticators.enable(row)
    row.changed_at = datetime.now(UTC)
    session.add(event("sensitive_update", account, client, ("passkey", str(row.id))))
    notices.notify(session, account, notices.Notice.PASSKEY_ENABLED, name=row.name)


async def erase(session: AsyncSession, account: Account, client: Client, actor: Account) -> None:
    """Delete an account, its authenticators and its sessions.

    Every address hears it.
    """
    notices.notify(session, account, notices.Notice.ACCOUNT_DELETED)
    target = ("account", str(account.id))
    session.add(
        events.event(
            "user_deleted",
            EventLevel.WARN,
            actor_id=actor.id,
            target_type=target[0],
            target_id=target[1],
            ip_address=client.ip_address,
            user_agent=client.user_agent,
        )
    )
    # The base deletes the rest; the connections of a session need it.
    await sessions.drop(session, AccountSession.account_id == account.id)
    await session.delete(account)


async def check_free(session: AsyncSession, column: sa.ColumnElement[bool]) -> None:
    """Answer 409 if an account already has the email or the phone."""
    if await session.scalar(sa.select(Account.id).where(column)) is not None:
        raise HTTPException(HTTPStatus.CONFLICT, "An account has it")


async def ask_email(session: AsyncSession, account: Account, email: str, client: Client) -> None:
    """Send a code to the new email of the account."""
    await check_free(session, Account.email == email)
    await limits.take(client, *codes.email_rules(email))
    code = await codes.issue(PURPOSE, f"{account.id}:{email}")
    codes.send_email(session, email, code, account.language)


async def ask_phone(
    session: AsyncSession, account: Account, phone: str, client: Client, host: str
) -> None:
    """Send a code to the new phone of the account."""
    await check_free(session, Account.phone == phone)
    await limits.take(client, *codes.sms_rules(phone, client))
    code = await codes.issue(PURPOSE, f"{account.id}:{phone}")
    codes.send_sms(session, phone, codes.sms_text(code, account.language, host, client.piece))


async def change_email(
    session: AsyncSession, account: Account, email: str, code: str, client: Client
) -> None:
    """Change the email with its code; notify the old one and all."""
    if not await codes.take(PURPOSE, f"{account.id}:{email}", code):
        raise AppError(INVALID_CODE)
    await check_free(session, Account.email == email)
    previous, account.email = account.email, email
    await recovery.reopen(session, account, Address.EMAIL, granted=False)
    details = events.changes("account", {"email": email})
    target = ("account", str(account.id))
    session.add(event("user_updated", account, client, target, details))
    notices.notify(session, account, notices.Notice.EMAIL_CHANGED, previous=previous)


async def change_phone(
    session: AsyncSession, account: Account, phone: str, code: str, client: Client
) -> None:
    """Change the phone with its code; notify the old one and all."""
    if not await codes.take(PURPOSE, f"{account.id}:{phone}", code):
        raise AppError(INVALID_CODE)
    await check_free(session, Account.phone == phone)
    previous, account.phone = account.phone, phone
    await sms.rebind(session, account)
    await recovery.reopen(session, account, Address.PHONE, granted=False)
    details = events.changes("account", {"phone": phone})
    target = ("account", str(account.id))
    session.add(event("user_updated", account, client, target, details))
    notices.notify(session, account, notices.Notice.PHONE_CHANGED, previous=previous)
