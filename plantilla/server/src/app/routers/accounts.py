"""The accounts that a superadmin manages: list, disable, recover."""

from datetime import datetime
from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query

from app.dependencies import ActingSuperadminDep, ClientDep, SessionDep, SuperadminDep
from app.enums import Address
from app.schemas.accounts import AccountFilter, AccountSummary, EmailSet, PhoneSet
from app.schemas.page import Page, decode_token, encode_token
from app.services import accounts

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("")
async def page(
    session: SessionDep, _: SuperadminDep, params: Annotated[AccountFilter, Query()]
) -> Page[AccountSummary]:
    """Page the accounts, oldest first, by an exact email or phone."""
    filters = {"email": params.email, "phone": params.phone}
    after = (
        decode_token(params.page_token, filters, tuple[datetime, UUID])
        if params.page_token
        else None
    )
    rows = await accounts.listing(session, params, after)
    full = len(rows) == params.page_size
    next_token = encode_token((rows[-1].created_at, rows[-1].id), filters) if full else ""
    return Page(
        items=[AccountSummary.model_validate(row) for row in rows], next_page_token=next_token
    )


# Declared before the routes of an account: "sessions" is no ID.
@router.delete("/sessions", status_code=HTTPStatus.NO_CONTENT)
async def close_all(
    session: SessionDep, principal: ActingSuperadminDep, caller: ClientDep
) -> None:
    """Close the sessions of every account but the one that calls."""
    await accounts.close_all(session, principal, caller)


@router.delete("/{account_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete(
    account_id: UUID, session: SessionDep, principal: ActingSuperadminDep, caller: ClientDep
) -> None:
    """Delete another account, its authenticators and its sessions."""
    target = await accounts.other(session, principal, account_id)
    await accounts.delete(session, principal, target, caller)


@router.post("/{account_id}/disable", status_code=HTTPStatus.NO_CONTENT)
async def disable(
    account_id: UUID, session: SessionDep, principal: ActingSuperadminDep, caller: ClientDep
) -> None:
    """Disable another account: it loses authenticators and sessions."""
    target = await accounts.other(session, principal, account_id)
    await accounts.disable(session, principal, target, caller)


@router.post("/{account_id}/enable", status_code=HTTPStatus.NO_CONTENT)
async def enable(
    account_id: UUID, session: SessionDep, principal: ActingSuperadminDep, caller: ClientDep
) -> None:
    """Enable a disabled account again; its holder recovers it."""
    target = await accounts.other(session, principal, account_id)
    await accounts.enable(session, principal, target, caller)


@router.put("/{account_id}/email", status_code=HTTPStatus.NO_CONTENT)
async def put_email(
    account_id: UUID,
    session: SessionDep,
    principal: ActingSuperadminDep,
    body: EmailSet,
    caller: ClientDep,
) -> None:
    """Give another account an email its holder has, to recover it."""
    target = await accounts.other(session, principal, account_id)
    await accounts.set_address(session, principal, target, (Address.EMAIL, body.email), caller)


@router.put("/{account_id}/phone", status_code=HTTPStatus.NO_CONTENT)
async def put_phone(
    account_id: UUID,
    session: SessionDep,
    principal: ActingSuperadminDep,
    body: PhoneSet,
    caller: ClientDep,
) -> None:
    """Give another account a phone its holder has, to recover it."""
    target = await accounts.other(session, principal, account_id)
    await accounts.set_address(session, principal, target, (Address.PHONE, body.phone), caller)


@router.delete("/{account_id}/sessions", status_code=HTTPStatus.NO_CONTENT)
async def close_sessions(
    account_id: UUID, session: SessionDep, principal: ActingSuperadminDep, caller: ClientDep
) -> None:
    """Close every session of another account."""
    target = await accounts.other(session, principal, account_id)
    await accounts.close_sessions(session, principal, target, caller)
