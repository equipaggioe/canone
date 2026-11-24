"""The password: signing in, authenticating again, adding it.

main.py mounts these routes only if the product offers the password.
"""

from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, Depends, Request, Response

from app.dependencies import ClientDep, PrincipalDep, ReauthenticatedDep, SessionDep, public
from app.routers.auth import RENEWED, open_cookie, open_token, renew
from app.schemas.auth import PasswordChange, PasswordLogin, PasswordReauth, TokenResponse
from app.services import passwords

router = APIRouter(tags=["password"])

ADDED: dict[int | str, dict[str, Any]] = {
    HTTPStatus.CREATED.value: {"description": "The account had no password"}
}


@router.post(
    "/auth/password/cookie", status_code=HTTPStatus.NO_CONTENT, dependencies=[Depends(public)]
)
async def cookie(
    request: Request,
    response: Response,
    session: SessionDep,
    body: PasswordLogin,
    caller: ClientDep,
) -> None:
    """Sign in the web with a password, in its cookie."""
    account = await passwords.check(session, body, caller)
    await open_cookie(request, response, session, account, caller)


@router.post("/auth/password/token", dependencies=[Depends(public)])
async def token(
    request: Request,
    response: Response,
    session: SessionDep,
    body: PasswordLogin,
    caller: ClientDep,
) -> TokenResponse:
    """Sign in an app with a password, as the token endpoint answers."""
    account = await passwords.check(session, body, caller)
    return await open_token(request, response, session, account, caller)


@router.post("/auth/reauth/password", response_model=TokenResponse, responses=RENEWED)
async def reauth(
    session: SessionDep, principal: PrincipalDep, body: PasswordReauth, caller: ClientDep
) -> Response:
    """Authenticate again with the password of the account."""
    holder = principal.account
    identifier = {"email": holder.email} if holder.email else {"phone": holder.phone}
    login = PasswordLogin.model_validate({**identifier, "password": body.password})
    await passwords.check(session, login, caller)
    return renew(session, principal, caller)


@router.put("/account/password", status_code=HTTPStatus.NO_CONTENT, responses=ADDED)
async def change(
    response: Response,
    session: SessionDep,
    principal: ReauthenticatedDep,
    body: PasswordChange,
    caller: ClientDep,
) -> None:
    """Add a password, or change it and close the other sessions."""
    if await passwords.put(session, principal, body.password, caller):
        response.status_code = HTTPStatus.CREATED
