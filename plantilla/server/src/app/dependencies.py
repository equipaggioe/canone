"""Dependencies shared by the routers."""

import re
from collections.abc import AsyncIterator, Callable
from datetime import UTC, datetime
from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, Response
from fastapi.dependencies.models import Dependant
from fastapi.routing import APIRoute, APIWebSocketRoute
from fastapi.security import APIKeyCookie, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import HTTPConnection

from app.config import VERSION, settings
from app.database import SessionFactory
from app.enums import EventLevel, Role, SessionKind
from app.errors import CLIENT_OUTDATED, REAUTHENTICATION_REQUIRED, AppError, KeptError
from app.services import channel, events, messages, sessions
from app.services.sessions import Client, Principal


async def get_session() -> AsyncIterator[AsyncSession]:
    """Open one session and one transaction per request.

    The transaction commits if the route ends or raises a KeptError, and
    rolls back on any other error. After the commit goes what the
    request queued: the WebSockets first, which wait for nobody.
    """
    kept: KeptError | None = None
    async with SessionFactory.begin() as session:
        try:
            yield session
        except KeptError as error:
            kept = error
    await channel.flush(session)
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


async def deny_by_default(connection: HTTPConnection) -> None:
    """Answer 404 to a route that does not say who may call it."""
    route = connection.scope.get("route")
    declares = isinstance(route, (APIRoute, APIWebSocketRoute)) and declares_access(
        route.dependant
    )
    if not declares:
        raise HTTPException(HTTPStatus.NOT_FOUND)


async def check_client_version(user_agent: Annotated[str, Header()] = "") -> None:
    """Reject an installable client older than its minimum version."""
    piece, _, version = user_agent.split(" ", 1)[0].partition("/")
    minimum = settings.min_client_versions.get(piece)
    # An empty tuple sorts first: a malformed version is outdated.
    if minimum is not None and version_numbers(version) < version_numbers(minimum):
        raise AppError(CLIENT_OUTDATED)


def client(connection: HTTPConnection) -> Client:
    """Tell where a request or a WebSocket comes from."""
    return Client(
        ip_address=connection.client.host if connection.client else None,
        user_agent=connection.headers.get("user-agent"),
    )


ClientDep = Annotated[Client, Depends(client)]

SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})


def needs_origin(connection: HTTPConnection) -> bool:
    """Tell whether the cookie makes the Origin matter.

    It does in an unsafe request, and in a handshake, unless it brings
    Authorization: then the cookie opens nothing.
    """
    if sessions.COOKIE not in connection.cookies:
        return False
    if connection.scope["type"] == "websocket":
        return "authorization" not in connection.headers
    return connection.scope["method"] not in SAFE_METHODS


async def check_origin(connection: HTTPConnection, caller: ClientDep) -> None:
    """Answer 403 to an unsafe request with the cookie from elsewhere.

    The server is the origin the request was sent to.
    """
    if not needs_origin(connection):
        return
    headers = connection.headers
    if headers.get("origin") != f"https://{headers.get('host')}":
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
async def handshake(connection: HTTPConnection, caller: ClientDep) -> Principal | None:
    """Recognize the session of a WebSocket, or none.

    It reads in its own session: one of the request would hold a
    connection to the database as long as the WebSocket.
    """
    header = connection.headers.get("authorization")
    if header is None:
        kind, token = SessionKind.WEB, connection.cookies.get(sessions.COOKIE, "")
    else:
        scheme, _, token = header.partition(" ")
        kind = SessionKind.APP
        if scheme.lower() != "bearer":
            return None
    async with SessionFactory.begin() as session:
        return await sessions.resolve(session, token, kind, caller)


HandshakeDep = Annotated[Principal | None, Depends(handshake)]


@access
async def reauthenticated(principal: PrincipalDep) -> Principal:
    """Require a session that authenticated within the last minutes."""
    if datetime.now(UTC) - principal.session.authenticated_at > sessions.REAUTHENTICATION:
        raise AppError(REAUTHENTICATION_REQUIRED)
    return principal


ReauthenticatedDep = Annotated[Principal, Depends(reauthenticated)]


@access
async def superadmin(request: Request, principal: PrincipalDep, caller: ClientDep) -> Principal:
    """Require the session of a superadmin; another account gets 403."""
    if principal.account.role != Role.SUPERADMIN:
        await events.record(
            events.event(
                "authz_fail",
                EventLevel.CRITICAL,
                actor_id=principal.account.id,
                target_type="route",
                target_id=request.url.path,
                ip_address=caller.ip_address,
                user_agent=caller.user_agent,
            )
        )
        raise HTTPException(HTTPStatus.FORBIDDEN, "Only a superadmin may do this")
    return principal


SuperadminDep = Annotated[Principal, Depends(superadmin)]


@access
async def reauthenticated_superadmin(principal: SuperadminDep) -> Principal:
    """Require a superadmin that authenticated within minutes."""
    return await reauthenticated(principal)


# ADR-0236: each change a superadmin makes asks a fresh authentication.
ActingSuperadminDep = Annotated[Principal, Depends(reauthenticated_superadmin)]
