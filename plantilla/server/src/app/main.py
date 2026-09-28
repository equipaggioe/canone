"""Create the app and mount the routers."""

from fastapi import FastAPI
from fastapi.routing import APIRoute

from app import errors, tracing


def operation_id(route: APIRoute) -> str:
    """Name each operation <tag>-<function>."""
    return f"{route.tags[0]}-{route.name}"


app = FastAPI(generate_unique_id_function=operation_id)
errors.install(app)
tracing.install(app)
