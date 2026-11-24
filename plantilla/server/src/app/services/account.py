"""The account of the session: its passkeys, its email and its phone."""

from datetime import datetime
from http import HTTPStatus
from uuid import UUID

import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from webauthn.helpers import base64url_to_bytes

from app.enums import EventLevel
from app.errors import INVALID_CODE, AppError
from app.models.account.account import Account
from app.models.account.passkey import Passkey
from app.models.event.event_log import EventLog
from app.schemas.account import PasskeyLink
from app.services import attestation, codes, events, limits, notices
from app.services.sessions import Client

PURPOSE = "change"


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
    details = events.changes("account", {"phone": phone})
    target = ("account", str(account.id))
    session.add(event("user_updated", account, client, target, details))
    notices.notify(session, account, notices.Notice.PHONE_CHANGED, previous=previous)
