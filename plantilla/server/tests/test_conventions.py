"""The conventions of fastapi.md and postgres.md in canone."""

import ast
import importlib
import pkgutil
import re
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType
from typing import Annotated, Any, TypeIs, get_args
from urllib.parse import urlsplit

import pytest
import sqlalchemy as sa
from fastapi import FastAPI, Query
from httpx import ASGITransport, AsyncClient
from pydantic import AwareDatetime, BaseModel

import app.models
import app.routers
import app.schemas
from app import errors, openapi, tracing
from app.config import Settings, settings
from app.database import engine
from app.dependencies import SessionDep
from app.main import app as main_app
from app.models.base import Base
from app.schemas.base import InputSchema, Schema, Timestamp
from app.schemas.page import decode_token, encode_token


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


def is_mapped(node: ast.AST) -> TypeIs[ast.AnnAssign]:
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
    """Tell whether a type holds a datetime that is not Timestamp."""
    if annotation == Timestamp:
        return False
    return annotation in (datetime, AwareDatetime) or any(
        mentions_datetime(arg) for arg in get_args(annotation)
    )


def test_schema_datetimes_are_timestamps() -> None:
    """Every date and time of a schema is Timestamp."""
    offenders = [
        f"{module.__name__}.{name}.{field_name}"
        for module in SCHEMA_MODULES
        for name, value in vars(module).items()
        if isinstance(value, type)
        and issubclass(value, BaseModel)
        and value.__module__ == module.__name__
        for field_name, field in value.model_fields.items()
        if mentions_datetime(
            Annotated[field.annotation, *field.metadata] if field.metadata else field.annotation
        )
    ]
    assert not offenders


def test_settings_are_required() -> None:
    """Every field of Settings is required and has no default."""
    offenders = [name for name, field in Settings.model_fields.items() if not field.is_required()]
    assert not offenders


def test_operation_ids() -> None:
    """Every operation has one tag and starts its camelCase ID by it."""
    offenders = [
        f"{method.upper()} {path}"
        for path, operations in main_app.openapi()["paths"].items()
        for method, operation in operations.items()
        if len(operation.get("tags", [])) != 1
        or not re.fullmatch(rf"{operation['tags'][0]}[A-Z][A-Za-z0-9]*", operation["operationId"])
    ]
    assert not offenders


def test_openapi_file_is_current() -> None:
    """openapi.json matches the app: python -m app.openapi."""
    assert openapi.FILE.read_text(encoding="utf-8") == openapi.render()


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
    assert body["type"] == errors.VALIDATION.uri
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
    assert response.json()["type"] == errors.CLIENT_OUTDATED.uri


async def test_problem_types_are_documented() -> None:
    """The URI of each problem type serves its documentation."""
    transport = ASGITransport(app=main_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for problem in errors.TYPES.values():
            response = await client.get(urlsplit(problem.uri).path)
            assert response.status_code == 200
            assert response.headers["content-type"].startswith("text/html")
            assert problem.title in response.text


async def test_invalid_page_token_points_to_the_parameter() -> None:
    """A bad page token, or one with other filters, is a 422."""
    probe = FastAPI()
    errors.install(probe)
    tracing.install(probe)
    position = (datetime(2026, 1, 1, tzinfo=UTC), 7)
    token = encode_token(position, {"status": "open"})
    assert decode_token(token, {"status": "open"}, tuple[datetime, int]) == position

    @probe.get("/items")
    async def list_items(
        page_token: Annotated[str, Query(alias="pageToken")], status: str
    ) -> None:
        """Read the page token with the filters of the request."""
        decode_token(page_token, {"status": status}, tuple[datetime, int])

    transport = ASGITransport(app=probe)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for params in (
            {"pageToken": token, "status": "closed"},
            {"pageToken": "x!", "status": "open"},
        ):
            response = await client.get("/items", params=params)
            assert response.status_code == 422
            assert response.json()["errors"] == [
                {"detail": "Invalid page token", "parameter": "pageToken"}
            ]


async def test_failed_commit_is_a_server_error() -> None:
    """A commit that fails answers 500, before any response."""
    probe = FastAPI()
    errors.install(probe)
    tracing.install(probe)

    @probe.post("/items")
    async def create_item(session: SessionDep) -> None:
        """Insert a duplicate that only the commit rejects."""
        await session.execute(
            sa.text(
                "CREATE TEMP TABLE item (id int UNIQUE DEFERRABLE INITIALLY DEFERRED)"
                " ON COMMIT DROP"
            )
        )
        await session.execute(sa.text("INSERT INTO item VALUES (1), (1)"))

    transport = ASGITransport(app=probe, raise_app_exceptions=False)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/items")
    finally:
        await engine.dispose()
    assert response.status_code == 500
    assert response.headers["content-type"] == errors.PROBLEM_JSON
