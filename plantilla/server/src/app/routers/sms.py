"""The code of an SMS: signing in, and authenticating again.

main.py mounts these routes only if the product offers the SMS code.
"""

from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from app.dependencies import ClientDep, PrincipalDep, SessionDep, public
from app.routers.auth import RENEWED, accepted, open_cookie, open_token, renew
from app.schemas.auth import SmsCode, SmsLogin, SmsReauth, TokenResponse
from app.services import sms

router = APIRouter(tags=["sms"])


@router.post("/auth/sms/code", status_code=HTTPStatus.NO_CONTENT, dependencies=[Depends(public)])
async def code(request: Request, session: SessionDep, body: SmsCode, caller: ClientDep) -> None:
    """Send the code to sign in to the phone of an account."""
    host = request.headers.get("host", "")
    await sms.send_code(session, body.phone, caller, accepted(request), host)


@router.post("/auth/sms/cookie", status_code=HTTPStatus.NO_CONTENT, dependencies=[Depends(public)])
async def cookie(
    request: Request,
    response: Response,
    session: SessionDep,
    body: SmsLogin,
    caller: ClientDep,
) -> None:
    """Sign in the web with the code of an SMS, in its cookie."""
    account = await sms.check(session, body.phone, body.code, caller)
    await open_cookie(request, response, session, account, caller)


@router.post("/auth/sms/token", dependencies=[Depends(public)])
async def token(
    request: Request,
    response: Response,
    session: SessionDep,
    body: SmsLogin,
    caller: ClientDep,
) -> TokenResponse:
    """Sign in an app with an SMS code, as the token endpoint."""
    account = await sms.check(session, body.phone, body.code, caller)
    return await open_token(request, response, session, account, caller)


@router.post("/auth/reauth/sms/code", status_code=HTTPStatus.NO_CONTENT)
async def reauth_code(
    request: Request, session: SessionDep, principal: PrincipalDep, caller: ClientDep
) -> None:
    """Send a code to the phone of the account, to reauthenticate."""
    phone = principal.account.phone
    if phone is None:
        raise HTTPException(HTTPStatus.CONFLICT, "The account has no phone")
    host = request.headers.get("host", "")
    await sms.send_code(session, phone, caller, accepted(request), host)


@router.post("/auth/reauth/sms", response_model=TokenResponse, responses=RENEWED)
async def reauth(
    session: SessionDep, principal: PrincipalDep, body: SmsReauth, caller: ClientDep
) -> Response:
    """Authenticate again with the code of the phone of the account."""
    phone = principal.account.phone
    if phone is None:
        raise HTTPException(HTTPStatus.CONFLICT, "The account has no phone")
    await sms.check(session, phone, body.code, caller)
    return renew(session, principal, caller)
