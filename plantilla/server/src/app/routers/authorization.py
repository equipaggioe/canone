"""The authorization code, for the desktop and for the web in its tab.

These routes answer a browser, not a generated client: they stay out of
the OpenAPI.
"""

from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from app import pages, translations
from app.dependencies import ClientDep, SessionDep, public
from app.schemas.authorization import Grant, Redirect
from app.services import authorization, clients, sessions
from app.translations import translation

router = APIRouter(
    prefix="/auth", tags=["authorization"], include_in_schema=False, dependencies=[Depends(public)]
)

FLOW_COOKIE = "__Host-flow"
# Neither the client nor its return may come repeated: the error could
# not go back.
UNTRUSTED = ("client_id", "redirect_uri")


def invalid(request: Request) -> HTMLResponse:
    """Show the error in the browser, without going to the client."""
    page = pages.invalid(translation(request.headers.get("accept-language", "")))
    return HTMLResponse(page, status_code=HTTPStatus.BAD_REQUEST)


def query(request: Request) -> tuple[dict[str, str], set[str]]:
    """Read the parameters: one without a value is absent.

    Return also the names that came more than once.
    """
    pairs = request.query_params.multi_items()
    names = [name for name, _ in pairs]
    repeated = {name for name in names if names.count(name) > 1}
    return {name: value for name, value in pairs if value}, repeated


def see_other(url: str) -> RedirectResponse:
    """Redirect with 303: a 307 would repeat a credential."""
    return RedirectResponse(url, status_code=HTTPStatus.SEE_OTHER)


@router.get("/authorize")
async def authorize(request: Request) -> Response:
    """Show the page that signs in with a passkey, on every request."""
    params, repeated = query(request)
    if repeated & set(UNTRUSTED):
        return invalid(request)
    try:
        waiting = authorization.read(params)
    except authorization.Invalid:
        return invalid(request)
    try:
        if repeated:
            raise authorization.Refused("invalid_request")
        authorization.check(waiting, params)
    except authorization.Refused as refused:
        return see_other(authorization.back(waiting, error=refused.code))
    key = await authorization.wait(waiting)
    page = pages.authorize(translation(request.headers.get("accept-language", "")), key)
    return HTMLResponse(page)


@router.post("/authorize")
async def grant(session: SessionDep, body: Grant, caller: ClientDep) -> Redirect:
    """Sign in a waiting request with its passkey, and give its code."""
    redirect = await authorization.grant(session, body.request, body.credential, caller)
    return Redirect(redirect=redirect)


@router.get("/web/start")
async def web_start(request: Request) -> Response:
    """Start the web flow: its state and verifier wait in Valkey."""
    key, url = await authorization.start_web(request.headers.get("host", ""))
    response = see_other(url)
    response.set_cookie(
        FLOW_COOKIE,
        key,
        max_age=int(authorization.LIFETIME.total_seconds()),
        path="/",
        secure=True,
        httponly=True,
        samesite="strict",
    )
    return response


@router.get("/web/return")
async def web_return(
    request: Request,
    session: SessionDep,
    caller: ClientDep,
    flow_key: Annotated[str | None, Cookie(alias=FLOW_COOKIE)] = None,
) -> Response:
    """Exchange the code of the web, set its cookie, go to the app."""
    params, _ = query(request)
    flow = await authorization.take_flow(flow_key) if flow_key else None
    if flow is None or "error" in params or params.get("state") != flow.state:
        response = invalid(request)
        response.delete_cookie(
            FLOW_COOKIE, path="/", secure=True, httponly=True, samesite="strict"
        )
        return response
    exchange = {
        "code": params.get("code", ""),
        "client_id": clients.WEB,
        "redirect_uri": clients.web_return(request.headers.get("host", "")),
        "code_verifier": flow.verifier,
    }
    account = await authorization.redeem(session, {k: v for k, v in exchange.items() if v})
    language = translations.language(request.headers.get("accept-language", ""))
    token, session_id = await sessions.open_web(session, account, caller, language)
    await authorization.spent(exchange["code"], session_id)
    response = see_other("/")
    response.delete_cookie(FLOW_COOKIE, path="/", secure=True, httponly=True, samesite="strict")
    sessions.set_cookie(response, token)
    return response
