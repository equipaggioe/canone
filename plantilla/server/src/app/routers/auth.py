"""Signing in, refreshing and signing out."""

from http import HTTPStatus
from typing import Any
from urllib.parse import parse_qsl

from fastapi import APIRouter, Depends, Request, Response

from app.dependencies import ClientDep, PrincipalDep, SessionDep, public
from app.enums import SessionKind, TokenErrorCode
from app.errors import PROBLEM_JSON, TokenRefusal
from app.schemas.auth import PasswordLogin, TokenError, TokenResponse
from app.services import passwords, sessions

router = APIRouter(prefix="/auth", tags=["auth"])

FORM = "application/x-www-form-urlencoded"
# RFC 6749: the tokens are not cached.
NO_STORE = {"Cache-Control": "no-store", "Pragma": "no-cache"}

TOKEN_FORM: dict[str, Any] = {
    "requestBody": {
        "required": True,
        "content": {
            FORM: {
                "schema": {
                    "type": "object",
                    "properties": {
                        "grant_type": {"type": "string", "enum": ["refresh_token"]},
                        "refresh_token": {"type": "string"},
                    },
                    "required": ["grant_type", "refresh_token"],
                }
            }
        },
    }
}
# The token endpoint answers its errors as RFC 6749; a client too old
# for the server is still a problem.
TOKEN_ERRORS: dict[int | str, dict[str, Any]] = {
    HTTPStatus.BAD_REQUEST.value: {
        "model": TokenError,
        "description": "Error of the token endpoint, or client outdated",
        "content": {PROBLEM_JSON: {"schema": {"$ref": "#/components/schemas/Problem"}}},
    }
}


def token_response(issued: sessions.Issued, response: Response) -> TokenResponse:
    """Answer the tokens of an app, not to be cached."""
    response.headers.update(NO_STORE)
    return TokenResponse(
        access_token=issued.access_token,
        token_type="Bearer",
        expires_in=int(sessions.ACCESS_LIFETIME.total_seconds()),
        refresh_token=issued.refresh_token,
    )


async def read_form(request: Request) -> dict[str, str]:
    """Read the parameters of the token endpoint.

    A parameter without a value is absent and one repeated is refused.
    """
    media_type = request.headers.get("content-type", "").partition(";")[0].strip().lower()
    if media_type != FORM:
        raise TokenRefusal(TokenErrorCode.INVALID_REQUEST)
    try:
        pairs = parse_qsl((await request.body()).decode(), keep_blank_values=True)
    except UnicodeDecodeError as error:
        raise TokenRefusal(TokenErrorCode.INVALID_REQUEST) from error
    names = [name for name, _ in pairs]
    if len(names) != len(set(names)):
        raise TokenRefusal(TokenErrorCode.INVALID_REQUEST)
    return {name: value for name, value in pairs if value}


def refresh_token(params: dict[str, str]) -> str:
    """Return the refresh token of a request, or refuse it."""
    if "grant_type" not in params:
        raise TokenRefusal(TokenErrorCode.INVALID_REQUEST)
    if "scope" in params:
        raise TokenRefusal(TokenErrorCode.INVALID_SCOPE)
    if params["grant_type"] != "refresh_token":
        raise TokenRefusal(TokenErrorCode.UNSUPPORTED_GRANT_TYPE)
    if "refresh_token" not in params:
        raise TokenRefusal(TokenErrorCode.INVALID_REQUEST)
    return params["refresh_token"]


@router.post("/password/cookie", status_code=HTTPStatus.NO_CONTENT, dependencies=[Depends(public)])
async def password_cookie(
    request: Request,
    response: Response,
    session: SessionDep,
    body: PasswordLogin,
    caller: ClientDep,
) -> None:
    """Sign in the web with a password, in its cookie.

    The cookie it brings is read from the request: the route does not
    require it.
    """
    account = await passwords.check(session, body, caller)
    presented = request.cookies.get(sessions.COOKIE)
    if presented is not None:
        await sessions.discard(session, presented, SessionKind.WEB)
    sessions.set_cookie(response, await sessions.open_web(session, account, caller))


@router.post("/password/token", dependencies=[Depends(public)])
async def password_token(
    request: Request,
    response: Response,
    session: SessionDep,
    body: PasswordLogin,
    caller: ClientDep,
) -> TokenResponse:
    """Sign in an app with a password, as the token endpoint answers.

    The access token it brings is read from the request: the route does
    not require it.
    """
    account = await passwords.check(session, body, caller)
    scheme, _, presented = request.headers.get("authorization", "").partition(" ")
    if scheme.lower() == "bearer" and presented:
        await sessions.discard(session, presented, SessionKind.APP)
    return token_response(await sessions.open_app(session, account, caller), response)


@router.post(
    "/token", responses=TOKEN_ERRORS, openapi_extra=TOKEN_FORM, dependencies=[Depends(public)]
)
async def token(
    request: Request, response: Response, session: SessionDep, caller: ClientDep
) -> TokenResponse:
    """Refresh the session of an app, rotating its refresh token."""
    presented = refresh_token(await read_form(request))
    return token_response(await sessions.refresh(session, presented, caller), response)


@router.post("/logout", status_code=HTTPStatus.NO_CONTENT)
async def logout(
    response: Response, session: SessionDep, principal: PrincipalDep, caller: ClientDep
) -> None:
    """Close the session that calls."""
    await sessions.close(session, principal.session, caller)
    if principal.session.kind == SessionKind.WEB:
        sessions.clear_cookie(response)
