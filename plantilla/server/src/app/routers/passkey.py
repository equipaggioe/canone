"""The passkey: signing in, again, linking, deleting and recovering.

main.py mounts these routes, and those of the authorization code, only
if the product offers the passkey.
"""

import secrets
from datetime import datetime
from http import HTTPStatus
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response

from app.dependencies import ClientDep, PrincipalDep, ReauthenticatedDep, SessionDep, public
from app.routers.auth import RENEWED, open_cookie, open_token, renew
from app.routers.recovery import RECOVERED, answer
from app.schemas.account import PasskeyLink, PasskeyView
from app.schemas.auth import (
    Identifier,
    PasskeyCreationOptions,
    PasskeyCredential,
    PasskeyOptions,
    PasskeyRecovery,
    RecoveryCodeView,
    RecoveryProof,
    TokenResponse,
)
from app.schemas.page import Page, PageParams, decode_token, encode_token
from app.services import account, attestation, passkeys, recovery

router = APIRouter(tags=["passkey"])

# transversal.md: a PUT that creates answers 201, and one repeated, 200.
FOUND: dict[int | str, dict[str, Any]] = {
    HTTPStatus.OK.value: {"model": PasskeyView, "description": "The passkey, already linked"}
}


@router.post("/auth/passkey/options", dependencies=[Depends(public)])
async def options() -> PasskeyOptions:
    """Start a login with a passkey: its challenge lives 10 minutes."""
    return await passkeys.options([])


@router.post(
    "/auth/passkey/cookie", status_code=HTTPStatus.NO_CONTENT, dependencies=[Depends(public)]
)
async def cookie(
    request: Request,
    response: Response,
    session: SessionDep,
    body: PasskeyCredential,
    caller: ClientDep,
) -> None:
    """Sign in the web with a passkey, in its cookie."""
    holder = await passkeys.check(session, body, caller)
    await open_cookie(request, response, session, holder, caller)


@router.post("/auth/passkey/token", dependencies=[Depends(public)])
async def token(
    request: Request,
    response: Response,
    session: SessionDep,
    body: PasskeyCredential,
    caller: ClientDep,
) -> TokenResponse:
    """Sign in an app with the passkey of its system."""
    holder = await passkeys.check(session, body, caller)
    return await open_token(request, response, session, holder, caller)


@router.post("/auth/register/options", dependencies=[Depends(public)])
async def creation(body: Identifier) -> PasskeyCreationOptions:
    """Start the passkey of a new account, with a new user handle."""
    return await attestation.options(secrets.token_bytes(64), body.address, [])


@router.post("/auth/reauth/options")
async def reauth_options(session: SessionDep, principal: PrincipalDep) -> PasskeyOptions:
    """Start authenticating again: the passkeys of the account."""
    return await passkeys.options(await account.all_passkeys(session, principal.account))


@router.post("/auth/reauth/passkey", response_model=TokenResponse, responses=RENEWED)
async def reauth(
    session: SessionDep, principal: PrincipalDep, body: PasskeyCredential, caller: ClientDep
) -> Response:
    """Authenticate again with a passkey of the account."""
    holder = await passkeys.check(session, body, caller)
    if holder.id != principal.account.id:
        raise HTTPException(HTTPStatus.FORBIDDEN, "The passkey is of another account")
    return renew(session, principal, caller)


@router.post("/account/passkeys/options")
async def link_options(session: SessionDep, principal: PrincipalDep) -> PasskeyCreationOptions:
    """Start a new passkey of the account."""
    holder = principal.account
    name = holder.email or holder.phone or ""
    existing = await account.all_passkeys(session, holder)
    return await attestation.options(holder.user_handle, name, existing)


@router.get("/account/passkeys")
async def page(
    session: SessionDep, principal: PrincipalDep, params: Annotated[PageParams, Query()]
) -> Page[PasskeyView]:
    """Page the passkeys of the account, with name and last use."""
    after = (
        decode_token(params.page_token, {}, tuple[datetime, UUID]) if params.page_token else None
    )
    rows = await account.passkeys(session, principal.account, after, params.page_size)
    full = len(rows) == params.page_size
    next_token = encode_token((rows[-1].created_at, rows[-1].id), {}) if full else ""
    return Page(
        items=[PasskeyView.model_validate(row) for row in rows], next_page_token=next_token
    )


@router.put("/account/passkeys/{passkey_id}", status_code=HTTPStatus.CREATED, responses=FOUND)
async def link(
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


@router.delete("/account/passkeys/{passkey_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete(
    passkey_id: UUID, session: SessionDep, principal: ReauthenticatedDep, caller: ClientDep
) -> None:
    """Delete a passkey of the account: a lost one stops working."""
    await account.unlink(session, principal.account, passkey_id, caller)


@router.post("/account/passkeys/{passkey_id}/enable", status_code=HTTPStatus.NO_CONTENT)
async def enable(
    passkey_id: UUID, session: SessionDep, principal: ReauthenticatedDep, caller: ClientDep
) -> None:
    """Enable a disabled passkey again: it binds it again."""
    await account.enable(session, principal.account, passkey_id, caller)


@router.post("/auth/recovery/options", dependencies=[Depends(public)])
async def recovery_options(
    session: SessionDep, body: RecoveryProof, caller: ClientDep
) -> PasskeyCreationOptions:
    """Start the passkey of a recovery; the code stays for the next."""
    return await recovery.options(session, body, caller)


@router.post(
    "/auth/recovery/passkey",
    response_model=RecoveryCodeView,
    responses=RECOVERED,
    dependencies=[Depends(public)],
)
async def recover(session: SessionDep, body: PasskeyRecovery, caller: ClientDep) -> Response:
    """Link a passkey with the code of the recovery."""
    return answer(await recovery.passkey(session, body, caller))
