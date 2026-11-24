"""Create the app and mount the routers."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI
from fastapi.routing import APIRoute

from app import errors, ijson, store, tracing
from app.database import engine
from app.dependencies import check_client_version, check_origin, deny_by_default
from app.enums import EventLevel, Method
from app.methods import METHODS
from app.routers import account, auth, authorization, health, passkey, password, problems
from app.services import events, messages


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
        await messages.client.aclose()


def api_router(methods: frozenset[Method]) -> APIRouter:
    """Mount the routers of /api: a method if the product has it."""
    api = APIRouter(
        prefix="/api",
        dependencies=[
            Depends(check_client_version),
            Depends(check_origin),
            Depends(deny_by_default),
        ],
        responses=errors.RESPONSES,
    )
    for router in (account.router, auth.router, health.router, problems.router):
        api.include_router(router)
    # The authorization code signs in with the passkey, on its page.
    if Method.PASSKEY in methods:
        api.include_router(passkey.router)
        api.include_router(authorization.router)
    if Method.PASSWORD in methods:
        api.include_router(password.router)
    return api


# ADR-0099: the telemetry stays in the process, whatever the
# environment says.
app = FastAPI(
    lifespan=lifespan,
    generate_unique_id_function=operation_id,
    telemetry={"auto_configure": False},
)
errors.install(app)
ijson.install(app)
tracing.install()
app.include_router(api_router(METHODS))
