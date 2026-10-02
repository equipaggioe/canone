"""Create the app and mount the routers."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI
from fastapi.routing import APIRoute

from app import errors, tracing
from app.database import engine
from app.dependencies import check_client_version
from app.routers import health


def operation_id(route: APIRoute) -> str:
    """Name each operation <tag>-<function>."""
    return f"{route.tags[0]}-{route.name}"


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    """Close the pooled connections when the server stops."""
    yield
    await engine.dispose()


api = APIRouter(prefix="/api", dependencies=[Depends(check_client_version)])
api.include_router(health.router)

app = FastAPI(lifespan=lifespan, generate_unique_id_function=operation_id)
errors.install(app)
tracing.install(app)
app.include_router(api)
