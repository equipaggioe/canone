"""Recover an account: the code sent, the saved code and the wait."""

import base64
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from http import HTTPStatus
from uuid import uuid4

import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.database import SessionFactory
from app.enums import Address, EventLevel, Role
from app.errors import INVALID_CODE, RECOVERY_DISABLED, AppError, KeptError
from app.models.account.account import Account
from app.models.account.passkey import Passkey
from app.models.account.password import Password
from app.models.account.recovery import Recovery
from app.models.account.recovery_address import RecoveryAddress
from app.models.account.recovery_code import RecoveryCode
from app.models.account.throttled import Throttled
from app.models.event.event_log import EventLog
from app.schemas.auth import (
    Identifier,
    PasskeyCreationOptions,
    PasskeyRecovery,
    PasswordRecovery,
    RecoveryProof,
)
from app.services import (
    attestation,
    authenticators,
    codes,
    events,
    limits,
    messages,
    notices,
    passwords,
)
from app.services.attestation import Created
from app.services.authenticators import WAIT_FROM
from app.services.sessions import Client

PURPOSE = "recover"
# A passkey account with only the code of its email waits this long.
DELAY = timedelta(hours=24)
# 80 random bits: 16 characters of base32.
SAVED_BYTES = 10


@dataclass(frozen=True)
class Outcome:
    """Whether a recovery waits, and the new saved code if any."""

    pending: bool
    recovery_code: str | None


def address_of(identifier: Identifier) -> Address:
    """Name the address a code goes to."""
    return Address.EMAIL if identifier.email is not None else Address.PHONE


def event(
    action: str, level: EventLevel, client: Client, account: Account | None, **details: object
) -> EventLog:
    """Build an event of the recovery of an account."""
    return events.event(
        action,
        level,
        actor_id=account.id if account else None,
        target_type="recovery",
        target_id=str(account.id) if account else None,
        ip_address=client.ip_address,
        user_agent=client.user_agent,
        details=details,
    )


async def find(session: AsyncSession, identifier: Identifier) -> Account | None:
    """Find the account of an email or a phone."""
    column = (
        Account.email == identifier.email
        if identifier.email
        else Account.phone == identifier.phone
    )
    return await session.scalar(sa.select(Account).where(column))


def refuse_superadmin(account: Account) -> None:
    """Answer 403 to a superadmin: another superadmin recovers it."""
    if account.role == Role.SUPERADMIN:
        raise HTTPException(HTTPStatus.FORBIDDEN, "A superadmin does not recover with a code")


async def way(session: AsyncSession, account: Account, address: Address) -> RecoveryAddress:
    """Lock the failures of an address, made if missing."""
    await session.execute(
        insert(RecoveryAddress)
        .values(account_id=account.id, address=address)
        .on_conflict_do_nothing()
    )
    row = await session.get(RecoveryAddress, (account.id, address), with_for_update=True)
    assert row is not None
    return row


async def admit(row: Throttled, client: Client, account: Account) -> None:
    """Refuse a way that is disabled, or before its wait."""
    if row.disabled_at is not None:
        raise AppError(RECOVERY_DISABLED)
    early = event("authn_login_fail_max", EventLevel.WARN, client, account, maxlimit=WAIT_FROM)
    await authenticators.admit(row, datetime.now(UTC), early)


def fail(session: AsyncSession, row: Throttled, client: Client, account: Account) -> KeptError:
    """Count a failure of a way, and answer 400 invalid-code."""
    disabled = authenticators.fail(row, datetime.now(UTC))
    session.add(event("authn_login_fail", EventLevel.WARN, client, account))
    if disabled:
        session.add(event("authn_login_lock", EventLevel.WARN, client, account, reason="failures"))
    return KeptError(AppError(INVALID_CODE))


async def send_code(
    session: AsyncSession, identifier: Identifier, client: Client, language: str, host: str
) -> None:
    """Send the code to recover to an address, or answer 404."""
    await codes.check_open(client)
    account = await find(session, identifier)
    if account is None:
        raise await codes.unknown(client)
    refuse_superadmin(account)
    address = address_of(identifier)
    await admit(await way(session, account, address), client, account)
    if address == Address.EMAIL:
        assert identifier.email is not None
        await limits.take(client, *codes.email_rules(identifier.email))
        code = await codes.issue(PURPOSE, identifier.email)
        codes.send_email(session, identifier.email, code, language)
        return
    assert identifier.phone is not None
    await limits.take(client, *codes.sms_rules(identifier.phone, client))
    code = await codes.issue(PURPOSE, identifier.phone)
    codes.send_sms(session, identifier.phone, codes.sms_text(code, language, host, client.piece))


async def check_saved(
    session: AsyncSession, account: Account, saved: str, client: Client
) -> RecoveryCode:
    """Return the saved code of the account if it is this one."""
    row = await session.get(RecoveryCode, account.id, with_for_update=True)
    if row is None:
        session.add(event("authn_login_fail", EventLevel.WARN, client, account, reason="no_code"))
        raise KeptError(AppError(INVALID_CODE))
    await admit(row, client, account)
    if not await run_in_threadpool(passwords.hasher.verify, saved, row.hash):
        raise fail(session, row, client, account)
    authenticators.succeed(row)
    return row


async def check(
    session: AsyncSession, proof: RecoveryProof, saved: str | None, client: Client
) -> tuple[Account, RecoveryCode | None]:
    """Return the account of a right code, and its saved code if sent.

    Each wrong code counts against its way. The code stays: the step
    that applies the recovery spends it.
    """
    account = await find(session, proof)
    if account is None:
        session.add(event("authn_login_fail", EventLevel.WARN, client, None))
        raise KeptError(AppError(INVALID_CODE))
    refuse_superadmin(account)
    row = await way(session, account, address_of(proof))
    await admit(row, client, account)
    if not await codes.take(PURPOSE, proof.address, proof.code, keep=True):
        raise fail(session, row, client, account)
    authenticators.succeed(row)
    found = await check_saved(session, account, saved, client) if saved is not None else None
    return account, found


def new_saved() -> str:
    """Make a saved code: 80 random bits in base32."""
    return base64.b32encode(secrets.token_bytes(SAVED_BYTES)).decode()


async def replace_saved(
    session: AsyncSession, account: Account, row: RecoveryCode | None
) -> tuple[str, bool]:
    """Make the saved code of the account; tell if it had none.

    A new code starts with no failures.
    """
    code = new_saved()
    digest = await run_in_threadpool(passwords.hash_password, code)
    if row is None:
        session.add(RecoveryCode(account_id=account.id, hash=digest))
        return code, True
    row.hash, row.created_at = digest, datetime.now(UTC)
    row.failures, row.retry_at, row.disabled_at = 0, None, None
    return code, False


async def create_saved(
    session: AsyncSession, account: Account, client: Client
) -> tuple[str, bool]:
    """Make the saved code that the holder asked for, and notify."""
    row = await session.get(RecoveryCode, account.id, with_for_update=True)
    code, new = await replace_saved(session, account, row)
    session.add(event("sensitive_create", EventLevel.INFO, client, account, kind="saved_code"))
    notices.notify(session, account, notices.Notice.RECOVERY_CODE_CREATED)
    return code, new


async def has_passkey(session: AsyncSession, account: Account) -> bool:
    """Tell whether the account has a passkey."""
    found = sa.select(sa.exists().where(Passkey.account_id == account.id))
    return bool(await session.scalar(found))


async def apply_password(
    session: AsyncSession, account: Account, digest: str, client: Client
) -> None:
    """Set the password of the account: it starts with no failures."""
    row = await session.get(Password, account.id, with_for_update=True)
    now = datetime.now(UTC)
    if row is None:
        session.add(Password(account_id=account.id, hash=digest, created_at=now, changed_at=now))
    else:
        row.hash, row.changed_at = digest, now
        row.failures, row.retry_at, row.disabled_at = 0, None, None
    passwords.changed(session, account, client)


def pend(
    account: Account,
    address: Address,
    password: str | None,
    created: Created | None,
    name: str | None,
) -> Recovery:
    """Write the recovery that waits, with its new authenticator."""
    row = Recovery(
        account_id=account.id,
        address=address,
        applies_at=datetime.now(UTC) + DELAY,
        password_hash=password,
    )
    if created is not None:
        row.credential_id, row.public_key = created.credential_id, created.public_key
        row.sign_count, row.uv_initialized = created.sign_count, created.user_verified
        row.transports, row.passkey_name = created.transports, name
        row.backup_eligible, row.backup_state = created.backup_eligible, created.backup_state
    return row


async def settle(
    session: AsyncSession,
    account: Account,
    proof: RecoveryProof,
    saved: RecoveryCode | None,
    client: Client,
    new: tuple[str | None, Created | None, str | None],
) -> Outcome:
    """Apply the recovery now, or in 24 hours, and notify every address.

    The saved code is spent and replaced. A passkey account with only
    the code of its email waits.
    """
    await codes.drop(PURPOSE, proof.address)
    password, created, name = new
    address = address_of(proof)
    replaced = (await replace_saved(session, account, saved))[0] if saved is not None else None
    if address == Address.EMAIL and saved is None and await has_passkey(session, account):
        await session.execute(sa.delete(Recovery).where(Recovery.account_id == account.id))
        session.add(pend(account, address, password, created, name))
        session.add(event("sensitive_create", EventLevel.WARN, client, account, address=address))
        notices.notify(session, account, notices.Notice.RECOVERY_PENDING)
        return Outcome(pending=True, recovery_code=None)
    if password is not None:
        await apply_password(session, account, password, client)
    if created is not None and name is not None:
        attestation.keep(session, account, created, name, uuid4(), client)
    notices.notify(session, account, notices.Notice.RECOVERED)
    return Outcome(pending=False, recovery_code=replaced)


async def password(session: AsyncSession, body: PasswordRecovery, client: Client) -> Outcome:
    """Reset or add the password with the code.

    A password on the blocklist keeps the code.
    """
    account, saved = await check(session, body, body.recovery_code, client)
    passwords.check_new(session, account, body.password, client)
    digest = await run_in_threadpool(passwords.hash_password, body.password)
    return await settle(session, account, body, saved, client, (digest, None, None))


async def options(
    session: AsyncSession, body: RecoveryProof, client: Client
) -> PasskeyCreationOptions:
    """Start the passkey of a recovery: the code opens the options.

    They carry the passkeys of the account, which only the code shows.
    """
    account, _ = await check(session, body, None, client)
    existing = list(
        await session.scalars(sa.select(Passkey).where(Passkey.account_id == account.id))
    )
    return await attestation.options(account.user_handle, body.address, existing)


async def passkey(session: AsyncSession, body: PasskeyRecovery, client: Client) -> Outcome:
    """Link a passkey with the code; the passkey is checked first."""
    created = await attestation.create(session, body.credential, client)
    account, saved = await check(session, body, body.recovery_code, client)
    if created.user_handle != account.user_handle:
        raise HTTPException(HTTPStatus.BAD_REQUEST, "The options were of another account")
    new = (None, created, body.passkey_name)
    return await settle(session, account, body, saved, client, new)


async def pending(session: AsyncSession, account: Account) -> Recovery | None:
    """Return the recovery of the account that waits, if any."""
    return await session.get(Recovery, account.id)


async def cancel(session: AsyncSession, account: Account, client: Client, reason: str) -> bool:
    """Delete the recovery that waits; tell whether there was one."""
    deleted = await session.execute(
        sa.delete(Recovery).where(Recovery.account_id == account.id).returning(Recovery.account_id)
    )
    if deleted.first() is None:
        return False
    session.add(event("sensitive_delete", EventLevel.INFO, client, account, reason=reason))
    return True


async def signed_in(session: AsyncSession, account: Account, client: Client) -> None:
    """Forget the failures of the recovery, and cancel what waits.

    Whoever signs in holds an authenticator of the account.
    """
    await session.execute(
        sa.delete(RecoveryAddress).where(RecoveryAddress.account_id == account.id)
    )
    await session.execute(
        sa.update(RecoveryCode)
        .where(RecoveryCode.account_id == account.id)
        .values(failures=0, retry_at=None, disabled_at=None)
    )
    await cancel(session, account, client, "sign_in")


def waiting_passkey(row: Recovery, account: Account) -> tuple[str, Created]:
    """Read the passkey of a recovery: its check keeps it whole."""
    assert row.credential_id is not None
    assert row.public_key is not None
    assert row.sign_count is not None
    assert row.uv_initialized is not None
    assert row.backup_eligible is not None
    assert row.backup_state is not None
    assert row.transports is not None
    assert row.passkey_name is not None
    return row.passkey_name, Created(
        user_handle=account.user_handle,
        credential_id=row.credential_id,
        public_key=row.public_key,
        sign_count=row.sign_count,
        user_verified=row.uv_initialized,
        backup_eligible=row.backup_eligible,
        backup_state=row.backup_state,
        transports=row.transports,
    )


async def apply(session: AsyncSession, row: Recovery, client: Client) -> None:
    """Apply a recovery whose wait ended, and notify every address.

    A passkey whose credential another account took meanwhile is left
    out, with its event.
    """
    account = await session.get(Account, row.account_id)
    assert account is not None
    await session.delete(row)
    if row.password_hash is not None:
        await apply_password(session, account, row.password_hash, client)
    elif row.credential_id is not None:
        taken = sa.select(sa.exists().where(Passkey.credential_id == row.credential_id))
        if await session.scalar(taken):
            session.add(
                event(
                    "input_validation_fail",
                    EventLevel.WARN,
                    client,
                    account,
                    reason="credential_taken",
                )
            )
            return
        name, created = waiting_passkey(row, account)
        attestation.keep(session, account, created, name, uuid4(), client)
    notices.notify(session, account, notices.Notice.RECOVERED)


async def apply_due() -> None:
    """Apply the recoveries whose 24 hours ended: the task recover."""
    client = Client(ip_address=None, user_agent=None)
    async with SessionFactory.begin() as session:
        due = await session.scalars(
            sa.select(Recovery)
            .where(Recovery.applies_at <= datetime.now(UTC))
            .with_for_update(skip_locked=True)
        )
        for row in list(due):
            await apply(session, row, client)
    await messages.flush(session)
