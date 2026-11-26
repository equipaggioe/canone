"""Register an account: its code, its authenticator and its role."""

import hmac
from datetime import timedelta
from http import HTTPStatus
from uuid import uuid4

import sqlalchemy as sa
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app import methods
from app.config import settings
from app.enums import EventLevel, Method, Role
from app.errors import INVALID_CODE, PASSWORD_BLOCKED, USER_VERIFICATION_REQUIRED, AppError
from app.models.account.account import Account
from app.models.account.password import Password
from app.schemas.auth import Identifier, Registration
from app.services import attestation, codes, events, limits, passwords, sms
from app.services.limits import Rule
from app.services.sessions import Client

PURPOSE = "register"
CONFLICTS = 10
CONFLICT_WINDOW = timedelta(minutes=15)
BLOCK = timedelta(minutes=30)
# Two registrations with the setup code wait for each other, so only
# one becomes the first superadmin.
SETUP_LOCK = 1


def block_key(client: Client) -> str:
    """Name the block of the registration of an IP."""
    return f"register:{client.ip_address}"


async def check_open(client: Client) -> None:
    """Answer 429 to an IP blocked by its 409 answers."""
    await limits.check_block(block_key(client), "Too many registrations of existing accounts")


async def check_new(session: AsyncSession, identifier: Identifier, client: Client) -> None:
    """Answer 409 if the account exists.

    The tenth 409 to an IP in 15 minutes blocks it 30 minutes.
    """
    taken = (
        Account.email == identifier.email
        if identifier.email
        else Account.phone == identifier.phone
    )
    if await session.scalar(sa.select(Account.id).where(taken)) is None:
        return
    rule = Rule(f"register:conflict:{client.ip_address}", CONFLICTS, CONFLICT_WINDOW, "")
    if await limits.hit(rule):
        await limits.block(block_key(client), BLOCK)
    raise HTTPException(HTTPStatus.CONFLICT, "The account exists")


async def send_code(
    session: AsyncSession, identifier: Identifier, client: Client, language: str, host: str
) -> None:
    """Send the code of a new account to its email or its phone.

    host is the web where the code is written.
    """
    await check_open(client)
    await check_new(session, identifier, client)
    if identifier.email is not None:
        await limits.take(client, *codes.email_rules(identifier.email))
        code = await codes.issue(PURPOSE, identifier.email)
        codes.send_email(session, identifier.email, code, language)
        return
    assert identifier.phone is not None
    await limits.take(client, *codes.sms_rules(identifier.phone, client))
    code = await codes.issue(PURPOSE, identifier.phone)
    text = codes.sms_text(code, language, host, client.piece)
    codes.send_sms(session, identifier.phone, text)


async def role(session: AsyncSession, setup_code: str | None) -> Role:
    """Return the role of a new account.

    The setup code makes a superadmin while there is none.
    """
    if setup_code is None:
        return Role.USER
    await session.execute(sa.select(sa.func.pg_advisory_xact_lock(SETUP_LOCK)))
    taken = await session.scalar(sa.select(sa.exists().where(Account.role == Role.SUPERADMIN)))
    if taken or not hmac.compare_digest(setup_code.encode(), settings.setup_code.encode()):
        raise HTTPException(HTTPStatus.FORBIDDEN, "The setup code is not accepted")
    return Role.SUPERADMIN


def check_offered(body: Registration) -> None:
    """Answer 422 to an authenticator the product does not offer.

    Without one, the account signs in with the code to its phone, where
    the product offers it.
    """
    if body.credential is not None:
        offered, field = Method.PASSKEY, "credential"
    elif body.password is not None:
        offered, field = Method.PASSWORD, "password"
    else:
        offered, field = Method.SMS, ""
    if offered in methods.METHODS and (offered != Method.SMS or body.phone is not None):
        return
    location = ("body", field) if field else ("body",)
    message = f"The product takes no {offered}" if field else "send a passkey or a password"
    raise RequestValidationError([{"loc": location, "msg": message, "type": "value_error"}])


async def register(
    session: AsyncSession, body: Registration, client: Client, language: str
) -> Account:
    """Create an account with its verified address and authenticator.

    Each authenticator only if the product offers it. The passkey is
    checked first: a failed ceremony leaves the code. The first
    superadmin brings the setup code instead of the code, and its
    address stays unverified. Where the registration is closed, only
    that superadmin registers.
    """
    await check_open(client)
    if body.code is not None and not methods.OPEN_REGISTRATION:
        raise HTTPException(HTTPStatus.FORBIDDEN, "A superadmin creates each account")
    created = None
    check_offered(body)
    if body.credential is not None:
        created = await attestation.create(session, body.credential, client)
    elif body.setup_code is not None and Method.PASSKEY in methods.METHODS:
        raise HTTPException(HTTPStatus.FORBIDDEN, "A superadmin registers with a passkey")
    elif body.password is not None and passwords.blocked(body.password):
        raise AppError(PASSWORD_BLOCKED)
    if body.code is not None and not await codes.take(PURPOSE, body.address, body.code):
        raise AppError(INVALID_CODE)
    await check_new(session, body, client)
    account_role = await role(session, body.setup_code)
    if account_role == Role.SUPERADMIN and created is not None and not created.user_verified:
        raise AppError(USER_VERIFICATION_REQUIRED)
    account = Account(email=body.email, phone=body.phone, role=account_role, language=language)
    if created is not None:
        account.user_handle = created.user_handle
    session.add(account)
    await session.flush()
    session.add(
        events.event(
            "user_created",
            EventLevel.INFO,
            actor_id=account.id,
            actor_label=body.address,
            target_type="account",
            target_id=str(account.id),
            ip_address=client.ip_address,
            user_agent=client.user_agent,
            details=events.changes("account", {"identifier": body.address, "role": account_role}),
        )
    )
    if body.phone is not None:
        sms.bind(session, account)
    if created is not None and body.passkey_name is not None:
        attestation.keep(session, account, created, body.passkey_name, uuid4(), client)
    if body.password is not None:
        digest = await run_in_threadpool(passwords.hash_password, body.password)
        session.add(Password(account_id=account.id, hash=digest))
        passwords.changed(session, account, client)
    return account
