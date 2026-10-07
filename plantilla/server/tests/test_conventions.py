"""The conventions of fastapi.md and postgres.md in canone."""

import ast
import importlib
import pkgutil
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType
from typing import Annotated, Any, get_args

import pytest
import sqlalchemy as sa
from fastapi import FastAPI, Query
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel

import app.models
import app.routers
import app.schemas
from app import errors, tracing
from app.config import settings
from app.database import engine
from app.main import app as main_app
from app.models.base import Base
from app.schemas.base import InputSchema, Schema
from app.schemas.page import decode_cursor, encode_cursor


def import_all(package: ModuleType) -> list[ModuleType]:
    """Import every module of a package."""
    return [
        importlib.import_module(module.name)
        for module in pkgutil.walk_packages(package.__path__, f"{package.__name__}.")
    ]


import_all(app.routers)
SCHEMA_MODULES = import_all(app.schemas)
TABLES = list(Base.metadata.tables.values())
COLUMNS = [column for table in TABLES for column in table.columns]
MODEL_FILES = sorted(Path(app.models.__path__[0]).glob("*/*.py"))


def is_allowed_key(column: sa.Column[Any]) -> bool:
    """Tell whether a key follows one of the rules of postgres.md."""
    if isinstance(column.type, sa.Text):
        return column.server_default is None and column.identity is None
    if isinstance(column.type, (sa.SmallInteger, sa.BigInteger)):
        return column.identity is not None and bool(column.identity.always)
    if isinstance(column.type, sa.Uuid):
        return str(getattr(column.server_default, "arg", "")) == "gen_random_uuid()"
    return False


def test_primary_key_is_allowed() -> None:
    """Every table has one key of the four rules of postgres.md."""
    offenders = [
        table.name
        for table in TABLES
        if len(table.primary_key.columns) != 1 or not is_allowed_key(table.primary_key.columns[0])
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
    """Every string column is created as TEXT."""
    offenders = [
        f"{column.table.name}.{column.name}"
        for column in COLUMNS
        if isinstance(column.type, sa.String)
        and column.type.compile(dialect=engine.dialect) != "TEXT"
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


def is_mapped(node: ast.AST) -> bool:
    """Tell whether a statement declares a column or a relationship."""
    return (
        isinstance(node, ast.AnnAssign)
        and isinstance(node.annotation, ast.Subscript)
        and getattr(node.annotation.value, "id", None) == "Mapped"
    )


def test_mapped_attributes_fit_one_line() -> None:
    """Every column and relationship is declared on one line."""
    offenders = [
        f"{path.parent.name}/{path.name}:{node.lineno}"
        for path in MODEL_FILES
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
        if is_mapped(node) and node.lineno != node.end_lineno
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


def mentions_datetime(annotation: Any) -> bool:
    """Tell whether a type is or contains a plain datetime."""
    return annotation is datetime or any(mentions_datetime(arg) for arg in get_args(annotation))


def test_schema_datetimes_are_aware() -> None:
    """Every date and time of a schema is AwareDatetime."""
    offenders = [
        f"{module.__name__}.{name}.{field_name}"
        for module in SCHEMA_MODULES
        for name, value in vars(module).items()
        if isinstance(value, type)
        and issubclass(value, BaseModel)
        and value.__module__ == module.__name__
        for field_name, field in value.model_fields.items()
        if mentions_datetime(field.annotation)
    ]
    assert not offenders


def test_operation_ids() -> None:
    """Every operation has one tag and the ID <tag>-<function>."""
    offenders = [
        f"{method.upper()} {path}"
        for path, operations in main_app.openapi()["paths"].items()
        for method, operation in operations.items()
        if len(operation.get("tags", [])) != 1
        or not operation["operationId"].startswith(f"{operation['tags'][0]}-")
    ]
    assert not offenders


async def test_unknown_route_is_a_problem() -> None:
    """A 404 leaves as problem+json."""
    transport = ASGITransport(app=main_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/no-such-route")
    assert response.status_code == 404
    assert response.headers["content-type"] == errors.PROBLEM_JSON
    body = response.json()
    assert len(body.pop("traceId")) == 32
    assert body == {"type": "about:blank", "title": "Not Found", "status": 404}


class Item(InputSchema):
    """A body with a two-word field."""

    item_name: str


async def test_validation_error_points_to_the_field() -> None:
    """A 422 points to the body field and the query parameter."""
    probe = FastAPI()
    errors.install(probe)
    tracing.install(probe)

    @probe.post("/items")
    async def create_item(item: Item, limit: Annotated[int, Query()]) -> None:
        """Accept an item."""

    transport = ASGITransport(app=probe)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/items", params={"limit": "x"}, json={"itemName": 1})
    assert response.status_code == 422
    assert response.headers["content-type"] == errors.PROBLEM_JSON
    body = response.json()
    assert body["type"] == errors.VALIDATION
    assert {error.get("pointer") or error.get("parameter") for error in body["errors"]} == {
        "/itemName",
        "limit",
    }


async def test_outdated_client_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    """A client below its minimum version gets client-outdated."""
    monkeypatch.setattr(settings, "min_client_versions", {"mobile": "1.4.0"})
    transport = ASGITransport(app=main_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health", headers={"User-Agent": "mobile/1.3.9"})
    assert response.status_code == 400
    assert response.headers["content-type"] == errors.PROBLEM_JSON
    assert response.json()["type"] == errors.CLIENT_OUTDATED


async def test_invalid_cursor_points_to_the_parameter() -> None:
    """A bad cursor, or one with other filters, is a 422."""
    probe = FastAPI()
    errors.install(probe)
    tracing.install(probe)
    position = (datetime(2026, 1, 1, tzinfo=UTC), 7)
    cursor = encode_cursor(position, {"status": "open"})
    assert decode_cursor(cursor, {"status": "open"}, tuple[datetime, int]) == position

    @probe.get("/items")
    async def list_items(cursor: str, status: str) -> None:
        """Read the cursor with the filters of the request."""
        decode_cursor(cursor, {"status": status}, tuple[datetime, int])

    transport = ASGITransport(app=probe)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for params in ({"cursor": cursor, "status": "closed"}, {"cursor": "x!", "status": "open"}):
            response = await client.get("/items", params=params)
            assert response.status_code == 422
            assert response.json()["errors"] == [
                {"detail": "Invalid cursor", "parameter": "cursor"}
            ]
