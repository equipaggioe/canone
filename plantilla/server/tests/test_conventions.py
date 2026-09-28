"""The conventions of fastapi.md and postgres.md in canone."""

import importlib
import pkgutil
from types import ModuleType
from typing import Annotated

import sqlalchemy as sa
from fastapi import FastAPI, Query
from fastapi.routing import APIRoute
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel

import app.models
import app.routers
import app.schemas
from app import errors
from app.main import app as main_app
from app.models.base import Base
from app.schemas.base import InputSchema, Schema


def import_all(package: ModuleType) -> list[ModuleType]:
    """Import every module of a package."""
    return [
        importlib.import_module(module.name)
        for module in pkgutil.walk_packages(package.__path__, f"{package.__name__}.")
    ]


import_all(app.models)
import_all(app.routers)
SCHEMA_MODULES = import_all(app.schemas)
TABLES = list(Base.metadata.tables.values())
COLUMNS = [column for table in TABLES for column in table.columns]


def test_primary_key_is_random_uuid() -> None:
    """Every table has one uuid key from gen_random_uuid()."""
    offenders = [
        table.name
        for table in TABLES
        if len(table.primary_key.columns) != 1
        or not isinstance(table.primary_key.columns[0].type, sa.Uuid)
        or str(getattr(table.primary_key.columns[0].server_default, "arg", ""))
        != "gen_random_uuid()"
    ]
    assert not offenders


def test_foreign_keys_declare_on_delete() -> None:
    """Every foreign key says CASCADE or RESTRICT."""
    offenders = [
        f"{key.parent.table.name}.{key.parent.name}"
        for table in TABLES
        for key in table.foreign_keys
        if key.ondelete not in ("CASCADE", "RESTRICT")
    ]
    assert not offenders


def test_foreign_keys_are_indexed() -> None:
    """Every foreign key column leads an index."""
    offenders = [
        f"{table.name}.{key.parent.name}"
        for table in TABLES
        for key in table.foreign_keys
        if not any(list(index.columns)[0] is key.parent for index in table.indexes)
    ]
    assert not offenders


def test_strings_are_text() -> None:
    """No string column has a maximum length."""
    offenders = [
        f"{column.table.name}.{column.name}"
        for column in COLUMNS
        if isinstance(column.type, sa.String) and column.type.length is not None
    ]
    assert not offenders


def test_datetimes_are_aware() -> None:
    """Every timestamp is timestamptz."""
    offenders = [
        f"{column.table.name}.{column.name}"
        for column in COLUMNS
        if isinstance(column.type, sa.DateTime) and not column.type.timezone
    ]
    assert not offenders


def test_enums_are_checked_text() -> None:
    """No column uses a native PostgreSQL enum."""
    offenders = [
        f"{column.table.name}.{column.name}"
        for column in COLUMNS
        if isinstance(column.type, sa.Enum) and column.type.native_enum
    ]
    assert not offenders


def test_relationships_raise() -> None:
    """Every relationship is declared with lazy="raise"."""
    offenders = [
        str(relationship)
        for mapper in Base.registry.mappers
        for relationship in mapper.relationships
        if relationship.lazy != "raise"
    ]
    assert not offenders


def test_schemas_inherit_schema() -> None:
    """Every schema inherits the camelCase base."""
    offenders = [
        f"{module.__name__}.{name}"
        for module in SCHEMA_MODULES
        for name, value in vars(module).items()
        if isinstance(value, type)
        and issubclass(value, BaseModel)
        and value.__module__ == module.__name__
        and not issubclass(value, Schema)
    ]
    assert not offenders


def test_operation_ids() -> None:
    """Every route has one tag and the ID <tag>-<function>."""
    offenders = [
        route.path
        for route in main_app.routes
        if isinstance(route, APIRoute)
        and (len(route.tags) != 1 or route.unique_id != f"{route.tags[0]}-{route.name}")
    ]
    assert not offenders


async def test_unknown_route_is_a_problem() -> None:
    """A 404 leaves as problem+json."""
    transport = ASGITransport(app=main_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/no-such-route")
    assert response.status_code == 404
    assert response.headers["content-type"] == errors.PROBLEM_JSON
    assert response.json() == {"type": "about:blank", "title": "Not Found", "status": 404}


class Item(InputSchema):
    """A body with a two-word field."""

    item_name: str


async def test_validation_error_points_to_the_field() -> None:
    """A 422 points to the body field and the query parameter."""
    probe = FastAPI()
    errors.install(probe)

    @probe.post("/items")
    async def create_item(item: Item, limit: Annotated[int, Query()]) -> None:
        """Accept an item."""

    transport = ASGITransport(app=probe)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/items", params={"limit": "x"}, json={"itemName": 1})
    assert response.status_code == 422
    assert response.headers["content-type"] == errors.PROBLEM_JSON
    body = response.json()
    assert {error.get("pointer") or error.get("parameter") for error in body["errors"]} == {
        "/itemName",
        "limit",
    }
