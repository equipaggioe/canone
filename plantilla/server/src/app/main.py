"""Create the app and mount the routers."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI
from fastapi.routing import APIRoute

from app import errors, ijson, store, tracing
from app.database import engine
from app.dependencies import check_client_version, check_origin, deny_by_default
from app.enums import EventLevel, Method, Push
from app.methods import METHODS, OPEN_REGISTRATION
from app.push import PUSH
from app.routers import (
    account,
    accounts,
    auth,
    authorization,
    fcm,
    health,
    passkey,
    password,
    problems,
    recovery,
    sms,
    web_push,
    websocket,
)
from app.schemas.websocket import CLIENT, SERVER
from app.services import events, transport
from app.services import web_push as web_push_service


def operation_id(route: APIRoute) -> str:
    """Name each operation by its tag and function, in camelCase."""
    first, *rest = f"{route.tags[0]}_{route.name}".split("_")
    return first + "".join(word.capitalize() for word in rest)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    """Log the start and the stop, and close the connections."""
    await events.record(events.event("sys_startup", EventLevel.WARN))
    yield
    try:
        await events.record(events.event("sys_shutdown", EventLevel.WARN))
    finally:
        await engine.dispose()
        await store.client.aclose()
        await transport.client.aclose()
        await web_push_service.client.aclose()


def api_router(
    methods: frozenset[Method], push: frozenset[Push], open_registration: bool
) -> APIRouter:
    """Mount the routers of /api: a method if the product has it.

    So with each service of push, and with the code of a new account.
    """
    api = APIRouter(
        prefix="/api",
        dependencies=[
            Depends(check_client_version),
            Depends(check_origin),
            Depends(deny_by_default),
        ],
        responses=errors.RESPONSES,
    )
    for router in (
        account.router,
        accounts.router,
        auth.router,
        health.router,
        problems.router,
        websocket.router,
    ):
        api.include_router(router)
    # The authorization code signs in with the passkey, on its page.
    if Method.PASSKEY in methods:
        api.include_router(passkey.router)
        api.include_router(authorization.router)
    if Method.PASSWORD in methods:
        api.include_router(password.router)
    if Method.SMS in methods:
        api.include_router(sms.router)
    # A recovery restores a passkey or a password.
    if methods & {Method.PASSKEY, Method.PASSWORD}:
        api.include_router(recovery.router)
    if open_registration:
        api.include_router(auth.signup)
    if Push.FCM in push:
        api.include_router(fcm.router)
    if Push.WEB in push:
        api.include_router(web_push.router)
    return api


# ADR-0099: the telemetry stays in the process, whatever the
# environment says.
app = FastAPI(
    lifespan=lifespan,
    generate_unique_id_function=operation_id,
    telemetry={"auto_configure": False},
)
errors.install(app)
# The messages of the WebSocket, which no route declares.
app.openapi = errors.with_schemas(  # pyrefly: ignore[method-assign]
    app.openapi,
    [(model, "validation") for model in CLIENT.values()]
    + [(model, "serialization") for model in SERVER],
)
ijson.install(app)
tracing.install()
app.include_router(api_router(METHODS, PUSH, OPEN_REGISTRATION))
