"""What a superadmin does to the other accounts.

Each action leaves authz_admin, besides the event of what it changed.
"""

from datetime import UTC, datetime
from http import HTTPStatus
from uuid import UUID

import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import Address, EventLevel, Role
from app.models.account.account import Account
from app.models.account.account_session import AccountSession
from app.models.account.passkey import Passkey
from app.models.account.password import Password
from app.models.account.recovery import Recovery
from app.models.account.recovery_address import RecoveryAddress
from app.models.account.recovery_code import RecoveryCode
from app.models.event.event_log import EventLog
from app.schemas.accounts import AccountCreate, AccountFilter
from app.services import account, events, notices, recovery, sessions, sms
from app.services.sessions import Client, Principal

# What a disabled account loses: its authenticators, and what recovers.
LOST = (Passkey, Password, RecoveryCode, Recovery, RecoveryAddress)


def admin_event(
    session: AsyncSession,
    principal: Principal,
    client: Client,
    what: str,
    target: tuple[str, str | None],
) -> None:
    """Log an action of a superadmin, with what it did."""
    session.add(
        events.event(
            "authz_admin",
            EventLevel.WARN,
            actor_id=principal.account.id,
            target_type=target[0],
            target_id=target[1],
            ip_address=client.ip_address,
            user_agent=client.user_agent,
            details={"event": what},
        )
    )


def changed(
    action: str, level: EventLevel, principal: Principal, client: Client, target: Account
) -> EventLog:
    """Build the event of an account that a superadmin changed."""
    return events.event(
        action,
        level,
        actor_id=principal.account.id,
        target_type="account",
        target_id=str(target.id),
        ip_address=client.ip_address,
        user_agent=client.user_agent,
    )


async def listing(
    session: AsyncSession, filters: AccountFilter, after: tuple[datetime, UUID] | None
) -> list[Account]:
    """Return a page of the accounts, oldest first, by address."""
    query = sa.select(Account)
    if filters.email is not None:
        query = query.where(Account.email == filters.email)
    if filters.phone is not None:
        query = query.where(Account.phone == filters.phone)
    if after is not None:
        query = query.where(sa.tuple_(Account.created_at, Account.id) > sa.tuple_(*after))
    query = query.order_by(Account.created_at, Account.id).limit(filters.page_size)
    return list(await session.scalars(query))


async def other(session: AsyncSession, principal: Principal, account_id: UUID) -> Account:
    """Return another account, locked; 404 if none, 403 if the caller's.

    A superadmin does not act on itself through these routes.
    """
    found = await session.get(Account, account_id, with_for_update=True)
    if found is None:
        raise HTTPException(HTTPStatus.NOT_FOUND)
    if found.id == principal.account.id:
        raise HTTPException(HTTPStatus.FORBIDDEN, "A superadmin does not act on itself here")
    return found


async def create(
    session: AsyncSession,
    principal: Principal,
    account_id: UUID,
    body: AccountCreate,
    context: tuple[Client, str],
) -> tuple[Account, bool]:
    """Create an account, with no authenticator, and say if it is new.

    Its holder takes it with the code of the recovery, at the address
    the superadmin set: a superadmin too, until it signs in. Repeated,
    it finds the same account; another one with the ID is a 409.
    """
    client, language = context
    found = await session.get(Account, account_id, with_for_update=True)
    if found is not None:
        if found.id == principal.account.id:
            raise HTTPException(HTTPStatus.FORBIDDEN, "A superadmin does not act on itself here")
        if (found.email, found.phone, found.role) != (body.email, body.phone, body.role):
            raise HTTPException(HTTPStatus.CONFLICT, "Another account has the ID")
        return found, False
    kind = Address.EMAIL if body.email is not None else Address.PHONE
    column = Account.email if kind == Address.EMAIL else Account.phone
    await account.check_free(session, column == body.address)
    target = Account(
        id=account_id, email=body.email, phone=body.phone, role=body.role, language=language
    )
    session.add(target)
    await session.flush()
    if body.phone is not None:
        sms.bind(session, target)
    await recovery.reopen(session, target, kind, granted=True)
    row = changed("user_created", EventLevel.INFO, principal, client, target)
    row.details = events.changes("account", {"identifier": body.address, "role": body.role})
    session.add(row)
    admin_event(session, principal, client, "user_created", ("account", str(target.id)))
    await notices.notify(session, target, notices.Notice.ACCOUNT_CREATED)
    return target, True


async def set_role(
    session: AsyncSession, principal: Principal, target: Account, role: Role, client: Client
) -> None:
    """Give another account a role; it rules from its next request.

    The same role changes nothing.
    """
    if target.role == role:
        return
    previous, target.role = target.role, role
    row = changed("authz_change", EventLevel.WARN, principal, client, target)
    row.details = {"from": previous.value, "to": role.value}
    session.add(row)
    admin_event(session, principal, client, "authz_change", ("account", str(target.id)))
    await notices.notify(session, target, notices.Notice.ROLE_CHANGED)


async def disable(
    session: AsyncSession, principal: Principal, target: Account, client: Client
) -> None:
    """Disable an account: it loses its authenticators and sessions.

    It keeps its email and its phone. One already disabled stays.
    """
    if target.disabled_at is not None:
        return
    # Before its sessions end: their devices hear it too.
    await notices.notify(session, target, notices.Notice.ACCOUNT_DISABLED)
    target.disabled_at = datetime.now(UTC)
    for model in LOST:
        await session.execute(sa.delete(model).where(model.account_id == target.id))
    closed = AccountSession.account_id == target.id
    await sessions.close_where(session, closed, client, "account_disabled")
    session.add(changed("user_archived", EventLevel.WARN, principal, client, target))
    admin_event(session, principal, client, "user_archived", ("account", str(target.id)))


async def enable(
    session: AsyncSession, principal: Principal, target: Account, client: Client
) -> None:
    """Enable a disabled account again, without what it lost."""
    if target.disabled_at is None:
        return
    target.disabled_at = None
    closed = AccountSession.account_id == target.id
    await sessions.close_where(session, closed, client, "account_disabled")
    row = changed("user_updated", EventLevel.INFO, principal, client, target)
    row.details = events.changes("account", {"disabled_at": None})
    session.add(row)
    admin_event(session, principal, client, "user_updated", ("account", str(target.id)))


async def delete(
    session: AsyncSession, principal: Principal, target: Account, client: Client
) -> None:
    """Delete another account, with every address notified."""
    admin_event(session, principal, client, "user_deleted", ("account", str(target.id)))
    await account.erase(session, target, client, principal.account)


async def set_address(
    session: AsyncSession,
    principal: Principal,
    target: Account,
    address: tuple[Address, str],
    client: Client,
) -> None:
    """Give an account an email or a phone that its holder has.

    The holder goes on with the code of the recovery: a superadmin
    takes it only at the address another superadmin set.
    """
    kind, value = address
    column = Account.email if kind == Address.EMAIL else Account.phone
    # A PUT repeated finds the same account with it.
    await account.check_free(session, (column == value) & (Account.id != target.id))
    if kind == Address.EMAIL:
        previous, target.email = target.email, value
        notice = notices.Notice.EMAIL_CHANGED
    else:
        previous, target.phone = target.phone, value
        await sms.rebind(session, target)
        notice = notices.Notice.PHONE_CHANGED
    await recovery.reopen(session, target, kind, granted=target.role == Role.SUPERADMIN)
    row = changed("user_updated", EventLevel.INFO, principal, client, target)
    row.details = events.changes("account", {kind.value: value})
    session.add(row)
    admin_event(session, principal, client, "user_updated", ("account", str(target.id)))
    await notices.notify(session, target, notice, previous=previous)


async def close_sessions(
    session: AsyncSession, principal: Principal, target: Account, client: Client
) -> None:
    """Close every session of another account."""
    closed = AccountSession.account_id == target.id
    await sessions.close_where(session, closed, client, "closed_by_admin")
    admin_event(session, principal, client, "session_logout", ("account", str(target.id)))


async def close_all(session: AsyncSession, principal: Principal, client: Client) -> None:
    """Close the sessions of every account but the one that calls."""
    others = AccountSession.id != principal.session.id
    await sessions.close_where(session, others, client, "closed_by_admin")
    admin_event(session, principal, client, "session_logout", ("account_session", None))
