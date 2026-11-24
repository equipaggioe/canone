"""Registering, refreshing, signing out, and what methods share."""

from http import HTTPStatus
from typing import Any
from urllib.parse import parse_qsl

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse

from app.dependencies import ClientDep, PrincipalDep, SessionDep, public
from app.enums import SessionKind, TokenErrorCode
from app.errors import PROBLEM_JSON, TokenRefusal
from app.models.account.account import Account
from app.schemas.auth import Identifier, Registration, TokenError, TokenResponse
from app.services import authorization, recovery, registration, sessions
from app.services.sessions import Client, Principal
from app.translations import language

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
                        "grant_type": {
                            "type": "string",
                            "enum": ["authorization_code", "refresh_token"],
                        },
                        "code": {"type": "string"},
                        "client_id": {"type": "string"},
                        "redirect_uri": {"type": "string"},
                        "code_verifier": {"type": "string"},
                        "refresh_token": {"type": "string"},
                    },
                    "required": ["grant_type"],
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
# Authenticating again answers as the session it renews: the tokens of
# an app, or the cookie of the web.
RENEWED: dict[int | str, dict[str, Any]] = {
    HTTPStatus.NO_CONTENT.value: {"description": "The web session, renewed in its cookie"}
}


def accepted(request: Request) -> str:
    """Choose the language of Accept-Language, or the base."""
    return language(request.headers.get("accept-language", ""))


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


def grant_type(params: dict[str, str]) -> str:
    """Return the grant of a request, or refuse it."""
    if "grant_type" not in params:
        raise TokenRefusal(TokenErrorCode.INVALID_REQUEST)
    if "scope" in params:
        raise TokenRefusal(TokenErrorCode.INVALID_SCOPE)
    if params["grant_type"] not in ("authorization_code", "refresh_token"):
        raise TokenRefusal(TokenErrorCode.UNSUPPORTED_GRANT_TYPE)
    return params["grant_type"]


async def open_cookie(
    request: Request, response: Response, session: SessionDep, account: Account, caller: Client
) -> None:
    """Open a web session in its cookie, closing the one it brings.

    The cookie is read from the request: the route does not require it.
    """
    presented = request.cookies.get(sessions.COOKIE)
    if presented is not None:
        await sessions.discard(session, presented, SessionKind.WEB)
    token, _ = await sessions.open_web(session, account, caller, accepted(request))
    await recovery.signed_in(session, account, caller)
    sessions.set_cookie(response, token)


async def open_token(
    request: Request, response: Response, session: SessionDep, account: Account, caller: Client
) -> TokenResponse:
    """Open an app session, closing the one of the token it brings.

    The token is read from the request: the route does not require it.
    """
    scheme, _, presented = request.headers.get("authorization", "").partition(" ")
    if scheme.lower() == "bearer" and presented:
        await sessions.discard(session, presented, SessionKind.APP)
    issued = await sessions.open_app(session, account, caller, accepted(request))
    await recovery.signed_in(session, account, caller)
    return token_response(issued, response)


@router.post(
    "/token", responses=TOKEN_ERRORS, openapi_extra=TOKEN_FORM, dependencies=[Depends(public)]
)
async def token(
    request: Request, response: Response, session: SessionDep, caller: ClientDep
) -> TokenResponse:
    """Exchange a code, or refresh a session, rotating its secret."""
    params = await read_form(request)
    if grant_type(params) == "refresh_token":
        presented = authorization.required(params, "refresh_token")
        return token_response(await sessions.refresh(session, presented, caller), response)
    account = await authorization.redeem(session, params)
    issued = await sessions.open_app(session, account, caller, accepted(request))
    await recovery.signed_in(session, account, caller)
    await authorization.spent(params["code"], issued.session_id)
    return token_response(issued, response)


@router.post("/logout", status_code=HTTPStatus.NO_CONTENT)
async def logout(
    response: Response, session: SessionDep, principal: PrincipalDep, caller: ClientDep
) -> None:
    """Close the session that calls."""
    await sessions.close(session, principal.session, caller)
    if principal.session.kind == SessionKind.WEB:
        sessions.clear_cookie(response)


@router.post("/register/code", status_code=HTTPStatus.NO_CONTENT, dependencies=[Depends(public)])
async def register_code(
    request: Request, session: SessionDep, body: Identifier, caller: ClientDep
) -> None:
    """Send the code of a new account to its email or its phone."""
    host = request.headers.get("host", "")
    await registration.send_code(session, body, caller, accepted(request), host)


@router.post("/register/cookie", status_code=HTTPStatus.NO_CONTENT, dependencies=[Depends(public)])
async def register_cookie(
    request: Request,
    response: Response,
    session: SessionDep,
    body: Registration,
    caller: ClientDep,
) -> None:
    """Register an account, and sign in the web."""
    account = await registration.register(session, body, caller, accepted(request))
    await open_cookie(request, response, session, account, caller)


@router.post("/register/token", dependencies=[Depends(public)])
async def register_token(
    request: Request,
    response: Response,
    session: SessionDep,
    body: Registration,
    caller: ClientDep,
) -> TokenResponse:
    """Register an account, and sign in an app."""
    account = await registration.register(session, body, caller, accepted(request))
    return await open_token(request, response, session, account, caller)


def renew(session: SessionDep, principal: Principal, caller: Client) -> Response:
    """Renew the session that authenticated again, by its kind."""
    if principal.session.kind == SessionKind.WEB:
        response = Response(status_code=HTTPStatus.NO_CONTENT)
        sessions.set_cookie(response, sessions.renew_web(session, principal.session, caller))
        return response
    issued = sessions.renew_app(session, principal.session, caller)
    body = token_response(issued, Response())
    return JSONResponse(body.model_dump(mode="json"), headers=NO_STORE)
