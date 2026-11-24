"""The account of the session: its email, its phone, its sessions."""

from datetime import datetime
from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Request, Response

from app.dependencies import ClientDep, PrincipalDep, ReauthenticatedDep, SessionDep
from app.enums import Role, SessionKind
from app.models.account.account_session import AccountSession
from app.schemas.account import (
    AccountView,
    EmailChange,
    EmailCode,
    FailureView,
    PhoneChange,
    PhoneCode,
    SessionView,
)
from app.schemas.page import Page, PageParams, decode_token, encode_token
from app.services import account, sessions

router = APIRouter(prefix="/account", tags=["account"])


@router.get("")
async def get(session: SessionDep, principal: PrincipalDep) -> AccountView:
    """Show the account, and whether each authenticator is disabled."""
    return await account.view(session, principal.account)


@router.delete("", status_code=HTTPStatus.NO_CONTENT)
async def delete(
    response: Response, session: SessionDep, principal: ReauthenticatedDep, caller: ClientDep
) -> None:
    """Delete the account, its authenticators and its sessions.

    Another superadmin deletes a superadmin.
    """
    if principal.account.role == Role.SUPERADMIN:
        raise HTTPException(HTTPStatus.FORBIDDEN, "Another superadmin deletes a superadmin")
    await account.erase(session, principal.account, caller, principal.account)
    if principal.session.kind == SessionKind.WEB:
        sessions.clear_cookie(response)


@router.get("/failures")
async def failures(
    session: SessionDep, principal: PrincipalDep, params: Annotated[PageParams, Query()]
) -> Page[FailureView]:
    """Page the failed attempts on the account, newest first."""
    after = (
        decode_token(params.page_token, {}, tuple[datetime, int]) if params.page_token else None
    )
    rows = await account.failures(session, principal.account, after, params.page_size)
    full = len(rows) == params.page_size
    next_token = encode_token((rows[-1].occurred_at, rows[-1].id), {}) if full else ""
    return Page(items=[account.failure(row) for row in rows], next_page_token=next_token)


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


@router.get("/sessions")
async def page_sessions(
    session: SessionDep, principal: PrincipalDep, params: Annotated[PageParams, Query()]
) -> Page[SessionView]:
    """Page the open sessions of the account, newest first."""
    after = (
        decode_token(params.page_token, {}, tuple[datetime, UUID]) if params.page_token else None
    )
    rows = await sessions.page(session, principal.account.id, after, params.page_size)
    full = len(rows) == params.page_size
    next_token = encode_token((rows[-1].created_at, rows[-1].id), {}) if full else ""
    items = [
        SessionView(
            id=row.id,
            kind=row.kind,
            user_agent=row.user_agent,
            created_at=row.created_at,
            last_used_at=row.last_used_at,
            current=row.id == principal.session.id,
        )
        for row in rows
    ]
    return Page(items=items, next_page_token=next_token)


@router.delete("/sessions", status_code=HTTPStatus.NO_CONTENT)
async def close_others(
    session: SessionDep, principal: ReauthenticatedDep, caller: ClientDep
) -> None:
    """Close every session of the account but the one that calls."""
    await sessions.close_others(session, principal.session, caller)


@router.delete("/sessions/{session_id}", status_code=HTTPStatus.NO_CONTENT)
async def close(
    session_id: UUID,
    response: Response,
    session: SessionDep,
    principal: ReauthenticatedDep,
    caller: ClientDep,
) -> None:
    """Close a session of the account; the one that calls signs out."""
    if session_id == principal.session.id:
        await sessions.close(session, principal.session, caller)
        if principal.session.kind == SessionKind.WEB:
            sessions.clear_cookie(response)
        return
    row = await session.get(AccountSession, session_id)
    if row is None or row.account_id != principal.account.id:
        raise HTTPException(HTTPStatus.NOT_FOUND)
    await sessions.close(session, row, caller)
