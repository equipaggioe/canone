"""Create the app and mount the routers."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI
from fastapi.routing import APIRoute

from app import errors, ijson, store, tracing
from app.database import engine
from app.dependencies import check_client_version, check_origin, deny_by_default
from app.enums import EventLevel
from app.routers import auth, health, problems
from app.services import events


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


api = APIRouter(
    prefix="/api",
    dependencies=[Depends(check_client_version), Depends(check_origin), Depends(deny_by_default)],
    responses=errors.RESPONSES,
)
api.include_router(auth.router)
api.include_router(health.router)
api.include_router(problems.router)

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
app.include_router(api)
