"""Dependencies shared by the routers."""

import re
from collections.abc import AsyncIterator, Callable
from datetime import UTC, datetime
from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, Response
from fastapi.dependencies.models import Dependant
from fastapi.routing import APIRoute
from fastapi.security import APIKeyCookie, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import VERSION, settings
from app.database import SessionFactory
from app.enums import EventLevel, SessionKind
from app.errors import CLIENT_OUTDATED, REAUTHENTICATION_REQUIRED, AppError, KeptError
from app.services import events, messages, sessions
from app.services.sessions import Client, Principal


async def get_session() -> AsyncIterator[AsyncSession]:
    """Open one session and one transaction per request.

    The transaction commits if the route ends or raises a KeptError, and
    rolls back on any other error. After the commit go the messages the
    request queued.
    """
    kept: KeptError | None = None
    async with SessionFactory.begin() as session:
        try:
            yield session
        except KeptError as error:
            kept = error
    await messages.flush(session)
    if kept is not None:
        raise kept.error


# Commit before the response, so a failed commit reaches the client.
SessionDep = Annotated[AsyncSession, Depends(get_session, scope="function")]


def version_numbers(version: str) -> tuple[int, ...]:
    """Split MAJOR.MINOR.PATCH into integers, or none if malformed."""
    if not re.fullmatch(VERSION, version):
        return ()
    return tuple(int(number) for number in version.split("."))


ACCESS = "__access__"


def access[F: Callable[..., object]](check: F) -> F:
    """Mark a dependency that says who may call a route."""
    setattr(check, ACCESS, True)
    return check


@access
async def public() -> None:
    """Let anyone call the route."""


def declares_access(dependant: Dependant) -> bool:
    """Tell whether a route or its dependencies say who calls it."""
    return any(
        getattr(sub.call, ACCESS, False) or declares_access(sub) for sub in dependant.dependencies
    )


async def deny_by_default(request: Request) -> None:
    """Answer 404 to a route that does not say who may call it."""
    route = request.scope.get("route")
    if not isinstance(route, APIRoute) or not declares_access(route.dependant):
        raise HTTPException(HTTPStatus.NOT_FOUND)


async def check_client_version(user_agent: Annotated[str, Header()] = "") -> None:
    """Reject an installable client older than its minimum version."""
    piece, _, version = user_agent.split(" ", 1)[0].partition("/")
    minimum = settings.min_client_versions.get(piece)
    # An empty tuple sorts first: a malformed version is outdated.
    if minimum is not None and version_numbers(version) < version_numbers(minimum):
        raise AppError(CLIENT_OUTDATED)


def client(request: Request) -> Client:
    """Tell where a request comes from."""
    return Client(
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )


ClientDep = Annotated[Client, Depends(client)]

SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})


async def check_origin(request: Request, caller: ClientDep) -> None:
    """Answer 403 to an unsafe request with the cookie from elsewhere.

    The server is the origin the request was sent to.
    """
    if sessions.COOKIE not in request.cookies or request.method in SAFE_METHODS:
        return
    if request.headers.get("origin") != f"https://{request.headers.get('host')}":
        await events.record(
            events.event(
                "malicious_csrf",
                EventLevel.WARN,
                ip_address=caller.ip_address,
                user_agent=caller.user_agent,
            )
        )
        raise HTTPException(HTTPStatus.FORBIDDEN, "The Origin is not the server")


bearer = HTTPBearer(auto_error=False)
session_cookie = APIKeyCookie(name=sessions.COOKIE, auto_error=False)


@access
async def signed_in(
    session: SessionDep,
    response: Response,
    caller: ClientDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    cookie: Annotated[str | None, Depends(session_cookie)],
) -> Principal:
    """Recognize the session of an app by its token, or of the web.

    A 401 to the cookie carries no WWW-Authenticate: the cookie is no
    authentication scheme of HTTP.
    """
    if credentials is not None:
        principal = await sessions.resolve(
            session, credentials.credentials, SessionKind.APP, caller
        )
        if principal is None:
            raise HTTPException(HTTPStatus.UNAUTHORIZED, headers={"WWW-Authenticate": "Bearer"})
        return principal
    if cookie is None:
        raise HTTPException(HTTPStatus.UNAUTHORIZED)
    principal = await sessions.resolve(session, cookie, SessionKind.WEB, caller)
    if principal is None:
        raise HTTPException(HTTPStatus.UNAUTHORIZED)
    if sessions.touch(principal.session):
        sessions.set_cookie(response, cookie)
    return principal


PrincipalDep = Annotated[Principal, Depends(signed_in)]


@access
async def reauthenticated(principal: PrincipalDep) -> Principal:
    """Require a session that authenticated within the last minutes."""
    if datetime.now(UTC) - principal.session.authenticated_at > sessions.REAUTHENTICATION:
        raise AppError(REAUTHENTICATION_REQUIRED)
    return principal


ReauthenticatedDep = Annotated[Principal, Depends(reauthenticated)]
