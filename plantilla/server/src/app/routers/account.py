"""The account of the session: its email and its phone."""

from http import HTTPStatus

from fastapi import APIRouter, Request

from app.dependencies import ClientDep, PrincipalDep, ReauthenticatedDep, SessionDep
from app.schemas.account import EmailChange, EmailCode, PhoneChange, PhoneCode
from app.services import account

router = APIRouter(prefix="/account", tags=["account"])


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
