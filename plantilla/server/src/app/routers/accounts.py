"""The accounts that a superadmin manages: create, list, disable."""

from datetime import datetime
from http import HTTPStatus
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Query, Request, Response

from app.dependencies import ActingSuperadminDep, ClientDep, SessionDep, SuperadminDep
from app.enums import Address
from app.schemas.accounts import (
    AccountCreate,
    AccountFilter,
    AccountSummary,
    EmailSet,
    PhoneSet,
    RoleSet,
)
from app.schemas.page import Page, decode_token, encode_token
from app.services import accounts
from app.translations import language

router = APIRouter(prefix="/accounts", tags=["accounts"])

# transversal.md: a PUT that creates answers 201, and one repeated, 200.
FOUND: dict[int | str, dict[str, Any]] = {
    HTTPStatus.OK.value: {"model": AccountSummary, "description": "The account, already created"}
}


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


@router.put("/{account_id}", status_code=HTTPStatus.CREATED, responses=FOUND)
async def create(
    account_id: UUID,
    request: Request,
    response: Response,
    session: SessionDep,
    principal: ActingSuperadminDep,
    body: AccountCreate,
    caller: ClientDep,
) -> AccountSummary:
    """Create an account its holder takes with the code of the recovery.

    It starts in the language of the superadmin, by the ID the client
    made.
    """
    context = (caller, language(request.headers.get("accept-language", "")))
    row, new = await accounts.create(session, principal, account_id, body, context)
    if not new:
        response.status_code = HTTPStatus.OK
    return AccountSummary.model_validate(row)


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


@router.put("/{account_id}/role", status_code=HTTPStatus.NO_CONTENT)
async def put_role(
    account_id: UUID,
    session: SessionDep,
    principal: ActingSuperadminDep,
    body: RoleSet,
    caller: ClientDep,
) -> None:
    """Give another account a role."""
    target = await accounts.other(session, principal, account_id)
    await accounts.set_role(session, principal, target, body.role, caller)


@router.delete("/{account_id}/sessions", status_code=HTTPStatus.NO_CONTENT)
async def close_sessions(
    account_id: UUID, session: SessionDep, principal: ActingSuperadminDep, caller: ClientDep
) -> None:
    """Close every session of another account."""
    target = await accounts.other(session, principal, account_id)
    await accounts.close_sessions(session, principal, target, caller)
