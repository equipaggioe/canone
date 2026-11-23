"""Signing in, refreshing and signing out."""

from http import HTTPStatus
from typing import Any
from urllib.parse import parse_qsl

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse

from app.dependencies import ClientDep, PrincipalDep, SessionDep, public
from app.enums import SessionKind, TokenErrorCode
from app.errors import PROBLEM_JSON, blank, respond
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


class Refused(Exception):
    """A request the token endpoint answers with an error."""

    def __init__(self, code: TokenErrorCode) -> None:
        """Keep the error code."""
        super().__init__(code.value)
        self.code = code


def token_error(code: TokenErrorCode) -> JSONResponse:
    """Answer an error of RFC 6749."""
    return JSONResponse(
        TokenError(error=code).model_dump(mode="json"), status_code=HTTPStatus.BAD_REQUEST
    )


def token_response(issued: sessions.Issued) -> JSONResponse:
    """Answer the tokens of an app, not to be cached."""
    body = TokenResponse(
        access_token=issued.access_token,
        token_type="Bearer",
        expires_in=int(sessions.ACCESS_LIFETIME.total_seconds()),
        refresh_token=issued.refresh_token,
    )
    return JSONResponse(body.model_dump(mode="json"), headers=NO_STORE)


def unauthorized() -> JSONResponse:
    """Answer a wrong password without raising, so its failure stays."""
    return respond(blank(HTTPStatus.UNAUTHORIZED))


async def read_form(request: Request) -> dict[str, str]:
    """Read the parameters of the token endpoint.

    A parameter without a value is absent and one repeated is refused.
    """
    media_type = request.headers.get("content-type", "").partition(";")[0].strip().lower()
    if media_type != FORM:
        raise Refused(TokenErrorCode.INVALID_REQUEST)
    try:
        pairs = parse_qsl((await request.body()).decode(), keep_blank_values=True)
    except UnicodeDecodeError as error:
        raise Refused(TokenErrorCode.INVALID_REQUEST) from error
    names = [name for name, _ in pairs]
    if len(names) != len(set(names)):
        raise Refused(TokenErrorCode.INVALID_REQUEST)
    return {name: value for name, value in pairs if value}


def refresh_token(params: dict[str, str]) -> str:
    """Return the refresh token of a request, or refuse it."""
    if "grant_type" not in params:
        raise Refused(TokenErrorCode.INVALID_REQUEST)
    if "scope" in params:
        raise Refused(TokenErrorCode.INVALID_SCOPE)
    if params["grant_type"] != "refresh_token":
        raise Refused(TokenErrorCode.UNSUPPORTED_GRANT_TYPE)
    if "refresh_token" not in params:
        raise Refused(TokenErrorCode.INVALID_REQUEST)
    return params["refresh_token"]


@router.post("/password/cookie", status_code=HTTPStatus.NO_CONTENT, dependencies=[Depends(public)])
async def password_cookie(
    request: Request, session: SessionDep, body: PasswordLogin, caller: ClientDep
) -> Response:
    """Sign in the web with a password, in its cookie.

    The cookie it brings is read from the request: the route does not
    require it.
    """
    account = await passwords.check(session, body, caller)
    if account is None:
        return unauthorized()
    presented = request.cookies.get(sessions.COOKIE)
    if presented is not None:
        await sessions.discard(session, presented, SessionKind.WEB)
    response = Response(status_code=HTTPStatus.NO_CONTENT)
    sessions.set_cookie(response, await sessions.open_web(session, account, caller))
    return response


@router.post("/password/token", response_model=TokenResponse, dependencies=[Depends(public)])
async def password_token(
    request: Request, session: SessionDep, body: PasswordLogin, caller: ClientDep
) -> Response:
    """Sign in an app with a password, as the token endpoint answers.

    The access token it brings is read from the request: the route does
    not require it.
    """
    account = await passwords.check(session, body, caller)
    if account is None:
        return unauthorized()
    scheme, _, presented = request.headers.get("authorization", "").partition(" ")
    if scheme.lower() == "bearer" and presented:
        await sessions.discard(session, presented, SessionKind.APP)
    return token_response(await sessions.open_app(session, account, caller))


@router.post(
    "/token",
    response_model=TokenResponse,
    responses=TOKEN_ERRORS,
    openapi_extra=TOKEN_FORM,
    dependencies=[Depends(public)],
)
async def token(request: Request, session: SessionDep, caller: ClientDep) -> Response:
    """Refresh the session of an app, rotating its refresh token.

    A reuse deletes the session in the transaction of the request: the
    error is answered, not raised.
    """
    try:
        presented = refresh_token(await read_form(request))
    except Refused as refused:
        return token_error(refused.code)
    issued = await sessions.refresh(session, presented, caller)
    if issued is None:
        return token_error(TokenErrorCode.INVALID_GRANT)
    return token_response(issued)


@router.post("/logout", status_code=HTTPStatus.NO_CONTENT)
async def logout(session: SessionDep, principal: PrincipalDep, caller: ClientDep) -> Response:
    """Close the session that calls."""
    await sessions.close(session, principal.session, caller)
    response = Response(status_code=HTTPStatus.NO_CONTENT)
    if principal.session.kind == SessionKind.WEB:
        sessions.clear_cookie(response)
    return response
