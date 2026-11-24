"""The account of the session: its passkeys, its email and its phone."""

from datetime import datetime
from http import HTTPStatus
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Query, Request, Response

from app.dependencies import ClientDep, PrincipalDep, ReauthenticatedDep, SessionDep
from app.schemas.account import (
    EmailChange,
    EmailCode,
    PasskeyLink,
    PasskeyView,
    PhoneChange,
    PhoneCode,
)
from app.schemas.auth import PasskeyCreationOptions
from app.schemas.page import Page, PageParams, decode_token, encode_token
from app.services import account, attestation

router = APIRouter(prefix="/account", tags=["account"])

# transversal.md: a PUT that creates answers 201, and one repeated, 200.
FOUND: dict[int | str, dict[str, Any]] = {
    HTTPStatus.OK.value: {"model": PasskeyView, "description": "The passkey, already linked"}
}


@router.post("/passkeys/options")
async def passkey_options(session: SessionDep, principal: PrincipalDep) -> PasskeyCreationOptions:
    """Start a new passkey of the account."""
    holder = principal.account
    name = holder.email or holder.phone or ""
    existing = await account.all_passkeys(session, holder)
    return await attestation.options(holder.user_handle, name, existing)


@router.get("/passkeys")
async def list_passkeys(
    session: SessionDep, principal: PrincipalDep, params: Annotated[PageParams, Query()]
) -> Page[PasskeyView]:
    """Page the passkeys of the account, with name and last use."""
    after = (
        decode_token(params.page_token, {}, tuple[datetime, UUID]) if params.page_token else None
    )
    rows = await account.passkeys(session, principal.account, after, params.page_size)
    full = len(rows) == params.page_size
    token = encode_token((rows[-1].created_at, rows[-1].id), {}) if full else ""
    return Page(items=[PasskeyView.model_validate(row) for row in rows], next_page_token=token)


@router.put("/passkeys/{passkey_id}", status_code=HTTPStatus.CREATED, responses=FOUND)
async def put_passkey(
    passkey_id: UUID,
    response: Response,
    session: SessionDep,
    principal: ReauthenticatedDep,
    body: PasskeyLink,
    caller: ClientDep,
) -> PasskeyView:
    """Link a passkey, by the ID the client made."""
    row, new = await account.link(session, principal.account, passkey_id, body, caller)
    if not new:
        response.status_code = HTTPStatus.OK
    return PasskeyView.model_validate(row)


@router.delete("/passkeys/{passkey_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_passkey(
    passkey_id: UUID, session: SessionDep, principal: ReauthenticatedDep, caller: ClientDep
) -> None:
    """Delete a passkey of the account: a lost one stops working."""
    await account.unlink(session, principal.account, passkey_id, caller)


@router.post("/email/code", status_code=HTTPStatus.NO_CONTENT)
async def email_code(
    session: SessionDep, principal: PrincipalDep, body: EmailCode, caller: ClientDep
) -> None:
    """Send a code to the new email of the account."""
    await account.ask_email(session, principal.account, body.email, caller)


@router.put("/email", status_code=HTTPStatus.NO_CONTENT)
async def put_email(
    session: SessionDep, principal: ReauthenticatedDep, body: EmailChange, caller: ClientDep
) -> None:
    """Change the email with the code it received."""
    await account.change_email(session, principal.account, body.email, body.code, caller)


@router.post("/phone/code", status_code=HTTPStatus.NO_CONTENT)
async def phone_code(
    request: Request,
    session: SessionDep,
    principal: PrincipalDep,
    body: PhoneCode,
    caller: ClientDep,
) -> None:
    """Send a code to the new phone of the account."""
    host = request.headers.get("host", "")
    await account.ask_phone(session, principal.account, body.phone, caller, host)


@router.put("/phone", status_code=HTTPStatus.NO_CONTENT)
async def put_phone(
    session: SessionDep, principal: ReauthenticatedDep, body: PhoneChange, caller: ClientDep
) -> None:
    """Change the phone with the code it received."""
    await account.change_phone(session, principal.account, body.phone, body.code, caller)
