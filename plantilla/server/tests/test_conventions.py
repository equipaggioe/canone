"""The conventions of fastapi.md and postgres.md in canone."""

import ast
import importlib
import json
import logging
import os
import pkgutil
import re
import subprocess
import sys
from datetime import UTC, date, datetime
from enum import Enum, StrEnum
from pathlib import Path
from types import ModuleType
from typing import Annotated, Any, TypeIs, get_args
from urllib.parse import urlsplit

import pytest
import sqlalchemy as sa
from fastapi import FastAPI, Query
from httpx import ASGITransport, AsyncClient
from pydantic import AwareDatetime, BaseModel, ValidationError
from pydantic_settings import BaseSettings
from sqlalchemy import orm
from sqlalchemy.dialects import postgresql

import app
import app.models
import app.routers
import app.schemas
from app import errors, ijson, openapi, tracing
from app.config import Settings, settings
from app.database import engine
from app.dependencies import SessionDep
from app.main import app as main_app
from app.models.base import Base
from app.schemas.base import Day, InputSchema, Schema, Timestamp
from app.schemas.page import decode_token, encode_token


def import_all(package: ModuleType) -> list[ModuleType]:
    """Import every module of a package."""
    return [
        importlib.import_module(module.name)
        for module in pkgutil.walk_packages(package.__path__, f"{package.__name__}.")
    ]


import_all(app.routers)
SCHEMA_MODULES = import_all(app.schemas)
APP_MODULES = import_all(app)
TABLES = list(Base.metadata.tables.values())
COLUMNS = [column for table in TABLES for column in table.columns]
MODEL_FILES = sorted(Path(app.models.__path__[0]).glob("*/*.py"))


def is_checked(column: sa.Column[Any]) -> bool:
    """Tell whether a CHECK of its table names the column."""
    return any(
        isinstance(constraint, sa.CheckConstraint)
        and re.search(rf"\b{column.name}\b", str(constraint.sqltext))
        for constraint in column.table.constraints
    )


def is_allowed_key(column: sa.Column[Any]) -> bool:
    """Tell whether a key follows one of the rules of postgres.md."""
    if isinstance(column.type, sa.Text):
        return column.server_default is None and column.identity is None and is_checked(column)
    if isinstance(column.type, sa.Integer) and not isinstance(column.type, sa.SmallInteger):
        return column.identity is not None and bool(column.identity.always)
    if isinstance(column.type, sa.Uuid):
        return str(getattr(column.server_default, "arg", "")) == "gen_random_uuid()"
    return False


def partition_columns(table: sa.Table) -> set[str]:
    """Return the columns that partition a table, if any."""
    partition = table.dialect_options["postgresql"].get("partition_by") or ""
    return set(re.findall(r"\w+", partition)) & set(table.columns.keys())


def extends_parent(column: sa.Column[Any]) -> bool:
    """Tell whether a key is a foreign key with CASCADE."""
    keys = column.foreign_keys
    return bool(keys) and all((key.ondelete or "").upper() == "CASCADE" for key in keys)


def is_allowed_primary_key(table: sa.Table) -> bool:
    """Tell whether a table key follows postgres.md."""
    columns = list(table.primary_key.columns)
    partition = partition_columns(table)
    if partition:
        rest = {column.name for column in columns[1:]}
        return bool(columns) and rest == partition and is_allowed_key(columns[0])
    if len(columns) == 1:
        return is_allowed_key(columns[0]) or extends_parent(columns[0])
    return len(columns) == 2 and all(
        column.foreign_keys or isinstance(column.type, sa.Text) for column in columns
    )


def test_primary_key_is_allowed() -> None:
    """Every table has a key of the rules of postgres.md."""
    offenders = [table.name for table in TABLES if not is_allowed_primary_key(table)]
    assert not offenders


def key_table(name: str, *items: sa.schema.SchemaItem, **options: Any) -> sa.Table:
    """Build a table apart from the models, to try a key on it."""
    metadata = sa.MetaData()
    sa.Table("account", metadata, sa.Column("id", sa.Uuid, primary_key=True))
    return sa.Table(name, metadata, *items, **options)


@pytest.mark.parametrize(
    ("table", "allowed"),
    [
        (
            key_table(
                "reading",
                sa.Column("id", sa.BigInteger, sa.Identity(always=True), primary_key=True),
                sa.Column("created_at", sa.DateTime(timezone=True), primary_key=True),
                postgresql_partition_by="RANGE (created_at)",
            ),
            True,
        ),
        (
            key_table(
                "reading",
                sa.Column("id", sa.BigInteger, primary_key=True),
                sa.Column("created_at", sa.DateTime(timezone=True), primary_key=True),
                postgresql_partition_by="RANGE (created_at)",
            ),
            False,
        ),
        (
            key_table(
                "unit",
                sa.Column("id", sa.SmallInteger, sa.Identity(always=True), primary_key=True),
            ),
            False,
        ),
        (
            key_table(
                "unit", sa.Column("id", sa.Integer, sa.Identity(always=True), primary_key=True)
            ),
            True,
        ),
        (
            key_table(
                "country",
                sa.Column("id", sa.Text, primary_key=True),
                sa.CheckConstraint("id ~ '^[A-Z]{2}$'", name="id"),
            ),
            True,
        ),
        (key_table("country", sa.Column("id", sa.Text, primary_key=True)), False),
        (key_table("country", sa.Column("id", sa.Text)), False),
        (
            key_table(
                "profile",
                sa.Column(
                    "account_id", sa.ForeignKey("account.id", ondelete="CASCADE"), primary_key=True
                ),
            ),
            True,
        ),
        (
            key_table(
                "profile",
                sa.Column(
                    "account_id",
                    sa.ForeignKey("account.id", ondelete="RESTRICT"),
                    primary_key=True,
                ),
            ),
            False,
        ),
        (
            key_table(
                "reading",
                sa.Column("created_at", sa.DateTime(timezone=True), primary_key=True),
                sa.Column("id", sa.BigInteger, sa.Identity(always=True), primary_key=True),
                postgresql_partition_by="RANGE (created_at)",
            ),
            False,
        ),
        (
            key_table(
                "grant",
                sa.Column("role", sa.Text, primary_key=True),
                sa.Column("permission", sa.Text, primary_key=True),
                sa.Column("scope", sa.Text, primary_key=True),
            ),
            False,
        ),
        (
            key_table(
                "role_permission",
                sa.Column("role", sa.Text, primary_key=True),
                sa.Column("permission", sa.Text, primary_key=True),
            ),
            True,
        ),
        (
            key_table(
                "membership",
                sa.Column("account_id", sa.ForeignKey("account.id"), primary_key=True),
                sa.Column("position", sa.Integer, primary_key=True),
            ),
            False,
        ),
    ],
)
def test_primary_key_rules(table: sa.Table, allowed: bool) -> None:
    """Check widths, codes, partitioned keys and natural keys."""
    assert is_allowed_primary_key(table) is allowed


def type_mismatches(tables: list[sa.Table]) -> list[str]:
    """Return the foreign keys of another type than their key."""
    dialect = postgresql.dialect()
    return [
        f"{key.parent.table.name}.{key.parent.name}"
        for table in tables
        for key in table.foreign_keys
        if key.parent.type.compile(dialect=dialect) != key.column.type.compile(dialect=dialect)
    ]


def test_foreign_keys_match_key_type() -> None:
    """Every foreign key has the type of the key it points to."""
    assert not type_mismatches(TABLES)


def test_foreign_key_type_mismatch() -> None:
    """A foreign key of another type is caught."""
    column = sa.Column("account_id", sa.Integer, sa.ForeignKey("account.id"))
    table = key_table("membership", column)
    assert type_mismatches([table]) == ["membership.account_id"]


def test_foreign_keys_declare_on_delete() -> None:
    """Every foreign key says CASCADE or RESTRICT."""
    offenders = [
        f"{key.parent.table.name}.{key.parent.name}"
        for table in TABLES
        for key in table.foreign_keys
        if (key.ondelete or "").upper() not in ("CASCADE", "RESTRICT")
    ]
    assert not offenders


def is_indexed(key: sa.ForeignKeyConstraint) -> bool:
    """Tell whether an index or a key leads with the key's columns."""
    names = {column.name for column in key.columns}
    table = key.table
    leads = [
        list(index.columns)
        for index in table.indexes
        if index.dialect_options["postgresql"]["where"] is None
    ]
    leads += [
        list(constraint.columns)
        for constraint in table.constraints
        if isinstance(constraint, (sa.PrimaryKeyConstraint, sa.UniqueConstraint))
    ]
    return any({column.name for column in lead[: len(names)]} == names for lead in leads)


def unindexed_keys(tables: list[sa.Table]) -> list[str]:
    """Return the foreign keys that no index leads."""
    return [
        f"{table.name}.({', '.join(key.column_keys)})"
        for table in tables
        for key in table.foreign_key_constraints
        if not is_indexed(key)
    ]


def test_foreign_keys_are_indexed() -> None:
    """Every foreign key leads an index or a key of its table."""
    assert not unindexed_keys(TABLES)


@pytest.mark.parametrize(
    ("table", "unindexed"),
    [
        (
            key_table(
                "membership",
                sa.Column("account_id", sa.Uuid, sa.ForeignKey("account.id"), primary_key=True),
                sa.Column("team", sa.Text, primary_key=True),
            ),
            [],
        ),
        (
            key_table(
                "membership",
                sa.Column("id", sa.Uuid, primary_key=True),
                sa.Column("account_id", sa.Uuid, sa.ForeignKey("account.id")),
                sa.Column("team", sa.Text),
                sa.Index("ix_membership_account_id", "account_id", "team"),
            ),
            [],
        ),
        (
            key_table(
                "membership",
                sa.Column("id", sa.Uuid, primary_key=True),
                sa.Column("account_id", sa.Uuid, sa.ForeignKey("account.id")),
            ),
            ["membership.(account_id)"],
        ),
        (
            key_table(
                "membership",
                sa.Column("team", sa.Text, primary_key=True),
                sa.Column("account_id", sa.Uuid, sa.ForeignKey("account.id"), primary_key=True),
            ),
            ["membership.(account_id)"],
        ),
    ],
)
def test_unindexed_key(table: sa.Table, unindexed: list[str]) -> None:
    """A key that leads no index is caught, even if one includes it."""
    assert unindexed_keys([table]) == unindexed


def element_type(column: sa.Column[Any]) -> Any:
    """Return the type of a column, or of the elements of its array."""
    kind = column.type
    return kind.item_type if isinstance(kind, sa.ARRAY) else kind


def test_strings_are_text() -> None:
    """Every string column, or array of strings, is created as TEXT."""
    offenders = [
        f"{column.table.name}.{column.name}"
        for column in COLUMNS
        if isinstance(element_type(column), sa.String)
        and element_type(column).compile(dialect=engine.dialect) != "TEXT"
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


def test_durations_are_seconds() -> None:
    """No column is an interval."""
    offenders = [
        f"{column.table.name}.{column.name}"
        for column in COLUMNS
        if isinstance(column.type, (sa.Interval, postgresql.INTERVAL))
    ]
    assert not offenders


def test_numerics_are_unscaled() -> None:
    """Every numeric has no precision and no scale."""
    offenders = [
        f"{column.table.name}.{column.name}"
        for column in COLUMNS
        if isinstance(column.type, sa.Numeric)
        and (column.type.precision is not None or column.type.scale is not None)
    ]
    assert not offenders


def is_allowed_geography(column: sa.Column[Any]) -> bool:
    """Tell whether a geography column follows postgres.md."""
    # geoalchemy2 has no type stubs.
    kind: Any = column.type
    return kind.srid == 4326


def geography_offenders(tables: list[sa.Table]) -> list[str]:
    """Return the spatial columns that break postgres.md."""
    from geoalchemy2 import Geography, Geometry

    return [
        f"{column.table.name}.{column.name}"
        for table in tables
        for column in table.columns
        if isinstance(column.type, Geometry)
        or (isinstance(column.type, Geography) and not is_allowed_geography(column))
    ]


def test_geography_columns() -> None:
    """Every spatial column is a WGS 84 geography."""
    pytest.importorskip("geoalchemy2")
    assert not geography_offenders(TABLES)


def is_unchecked_enum(column: sa.Column[Any]) -> bool:
    """Tell whether an enum or enum array is native or unchecked."""
    kind = element_type(column)
    if not isinstance(kind, sa.Enum):
        return False
    if isinstance(column.type, sa.ARRAY):
        return kind.native_enum or not is_checked(column)
    return kind.native_enum or not kind.create_constraint


def test_enums_are_checked_text() -> None:
    """Every enum, also in an array, is text with a CHECK."""
    offenders = [
        f"{column.table.name}.{column.name}" for column in COLUMNS if is_unchecked_enum(column)
    ]
    assert not offenders


def test_single_keys_are_id() -> None:
    """A one-column key that is no foreign key is called id."""
    offenders = [
        table.name
        for table in TABLES
        if len(table.primary_key.columns) == 1
        and not next(iter(table.primary_key.columns)).foreign_keys
        and next(iter(table.primary_key.columns)).name != "id"
    ]
    assert not offenders


def test_timestamps_have_suffix() -> None:
    """Every timestamptz column ends in _at, _from or _until."""
    offenders = [
        f"{column.table.name}.{column.name}"
        for column in COLUMNS
        if isinstance(column.type, sa.DateTime)
        and not column.name.endswith(("_at", "_from", "_until"))
    ]
    assert not offenders


def test_tables_avoid_pg_prefix() -> None:
    """No table name starts with pg_."""
    assert not [table.name for table in TABLES if table.name.startswith("pg_")]


def key_columns(table: sa.Table) -> list[list[str]]:
    """Return the columns of each primary key and UNIQUE of a table."""
    return [
        [column.name for column in constraint.columns]
        for constraint in table.constraints
        if isinstance(constraint, (sa.PrimaryKeyConstraint, sa.UniqueConstraint))
    ]


def test_keys_have_no_twin_index() -> None:
    """No index repeats the columns of a primary key or a UNIQUE."""
    offenders = [
        index.name
        for table in TABLES
        for index in table.indexes
        if index.dialect_options["postgresql"]["where"] is None
        and [column.name for column in index.columns] in key_columns(table)
    ]
    assert not offenders


def test_json_is_jsonb() -> None:
    """Every JSON document is jsonb."""
    offenders = [
        f"{column.table.name}.{column.name}"
        for column in COLUMNS
        if isinstance(column.type, sa.JSON) and not isinstance(column.type, postgresql.JSONB)
    ]
    assert not offenders


def test_integers_are_not_small() -> None:
    """No column is a smallint."""
    offenders = [
        f"{column.table.name}.{column.name}"
        for column in COLUMNS
        if isinstance(column.type, sa.SmallInteger)
    ]
    assert not offenders


def test_amounts_are_not_money() -> None:
    """No column is money."""
    offenders = [
        f"{column.table.name}.{column.name}"
        for column in COLUMNS
        if isinstance(column.type, postgresql.MONEY)
    ]
    assert not offenders


def test_times_have_no_zone() -> None:
    """No column is a time with time zone."""
    offenders = [
        f"{column.table.name}.{column.name}"
        for column in COLUMNS
        if isinstance(column.type, sa.Time) and column.type.timezone
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


def deletes_by_database(relationship: orm.RelationshipProperty[Any]) -> bool:
    """Tell whether a one-to-many leaves the delete to its ON DELETE."""
    child_columns = [remote for _, remote in relationship.local_remote_pairs or []]
    rules = {key.ondelete for column in child_columns for key in column.foreign_keys}
    if rules == {"CASCADE"}:
        owned = {"save-update", "merge", "delete", "delete-orphan"}
        return set(relationship.cascade) == owned and relationship.passive_deletes is True
    return relationship.passive_deletes == "all" and "delete" not in relationship.cascade


def test_one_to_many_leaves_deletes_to_the_database() -> None:
    """A one-to-many lets ON DELETE cascade or restrict, not the ORM."""
    offenders = [
        str(relationship)
        for mapper in Base.registry.mappers
        for relationship in mapper.relationships
        if relationship.direction is orm.ONETOMANY and not deletes_by_database(relationship)
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


def defined_classes(base: type) -> list[type]:
    """Return the subclasses of base that the app defines."""
    return [
        value
        for module in APP_MODULES
        for value in vars(module).values()
        if isinstance(value, type)
        and issubclass(value, base)
        and value.__module__ == module.__name__
    ]


def test_schemas_inherit_schema() -> None:
    """Every schema of the app inherits the camelCase base."""
    offenders = [
        model.__qualname__
        for model in defined_classes(BaseModel)
        if not issubclass(model, (Schema, BaseSettings))
    ]
    assert not offenders


def test_enums_are_strenums() -> None:
    """Every enum of the app inherits StrEnum."""
    offenders = [
        kind.__qualname__ for kind in defined_classes(Enum) if not issubclass(kind, StrEnum)
    ]
    assert not offenders


class Row:
    """An object with a two-word attribute, like a row."""

    created_at = datetime(2026, 1, 1, tzinfo=UTC)


class Created(Schema):
    """A response with a two-word field."""

    created_at: Timestamp


class CreatedInput(InputSchema):
    """A body with a two-word field."""

    created_at: Timestamp


def test_schemas_read_rows_by_name() -> None:
    """A response reads created_at of a row; a body only createdAt."""
    assert Created.model_validate(Row()).model_dump() == {"createdAt": Row.created_at}
    with pytest.raises(ValidationError):
        CreatedInput.model_validate({"created_at": "2026-01-01T00:00:00Z"})


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
        if mentions_datetime(field.rebuild_annotation())
    ]
    assert not offenders


def mentions_date(annotation: Any) -> bool:
    """Tell whether a type holds a time-free date other than Day."""
    if annotation == Day:
        return False
    return annotation is date or any(mentions_date(arg) for arg in get_args(annotation))


def test_schema_dates_are_days() -> None:
    """Every date without a time of a schema is Day."""
    offenders = [
        f"{module.__name__}.{name}.{field_name}"
        for module in SCHEMA_MODULES
        for name, value in vars(module).items()
        if isinstance(value, type)
        and issubclass(value, BaseModel)
        and value.__module__ == module.__name__
        for field_name, field in value.model_fields.items()
        if mentions_date(field.rebuild_annotation())
    ]
    assert not offenders


class Born(InputSchema):
    """A body with a date without a time."""

    born_on: Day


@pytest.mark.parametrize("value", [1767830400, "2026-01-08T00:00:00Z", "20260108", "2026-1-8"])
def test_day_takes_only_a_full_date(value: object) -> None:
    """Day reads only YYYY-MM-DD, and writes it back the same way."""
    assert Born.model_validate_json('{"bornOn": "2026-01-08"}').model_dump_json() == (
        '{"bornOn":"2026-01-08"}'
    )
    with pytest.raises(ValidationError):
        Born.model_validate_json(json.dumps({"bornOn": value}))


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


def problem_schema(status: str) -> dict[str, Any]:
    """Return the only content an error may declare, by its status."""
    name = "ValidationProblem" if status == "422" else "Problem"
    return {errors.PROBLEM_JSON: {"schema": {"$ref": f"#/components/schemas/{name}"}}}


def test_errors_are_problems() -> None:
    """Every operation declares its errors as problem+json.

    Each with the schema of its problem: a 422 with the validation
    one.
    """
    document = main_app.openapi()
    offenders = [
        f"{method.upper()} {path} {status}"
        for path, operations in document["paths"].items()
        for method, operation in operations.items()
        for status in {"4XX", "5XX"} | set(operation["responses"])
        if status[0] in "45"
        and operation["responses"].get(status, {}).get("content") != problem_schema(status)
    ]
    assert not offenders


def test_problems_let_extensions_through() -> None:
    """No schema of a problem forbids other members."""
    schemas = main_app.openapi()["components"]["schemas"]
    for name in ("Problem", "ValidationProblem", "FieldError"):
        assert "additionalProperties" not in schemas[name]


def test_log_lines_have_no_line_breaks() -> None:
    """A value with a line break stays on one line of the log."""
    record = logging.LogRecord("app", logging.INFO, __file__, 1, "got %s", ("a\r\nb",), None)
    handler = tracing.log_handler()
    assert handler.filter(record)
    assert handler.format(record) == "INFO app  got a\\r\\nb"


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


async def test_traceparent_starts_a_new_trace() -> None:
    """The client does not pick the trace-id."""
    sent = "4bf92f3577b34da6a3ce929d0e0e4736"
    transport = ASGITransport(app=main_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/no-such-route", headers={"traceparent": f"00-{sent}-00f067aa0ba902b7-01"}
        )
    assert response.json()["traceId"] not in (sent, "")


# Starts and stops the app, and prints how many span processors it
# added and whether it configures itself from the environment: without
# the OTLP exporter installed, it adds none either way. FastAPI reads
# FASTAPI_OTEL_AUTO_CONFIGURE when it builds the app, so the probe
# imports it in a process of its own.
TELEMETRY_PROBE = """
import asyncio
from opentelemetry.sdk.trace import TracerProvider
added = []
TracerProvider.add_span_processor = lambda _, processor: added.append(processor)
from app.main import app
from app.services import events
async def skip(row):
    pass
events.record = skip
messages = iter([{"type": "lifespan.startup"}, {"type": "lifespan.shutdown"}])
async def receive():
    return next(messages)
async def send(message):
    pass
asyncio.run(app({"type": "lifespan", "asgi": {"version": "3.0"}}, receive, send))
print(len(added), app._telemetry["auto_configure"])
"""


def test_otlp_variables_export_nothing() -> None:
    """The app adds no exporter, whatever the OTLP variables say."""
    environment = os.environ | {
        "FASTAPI_OTEL_AUTO_CONFIGURE": "true",
        "OTEL_EXPORTER_OTLP_ENDPOINT": "http://127.0.0.1:4318",
    }
    result = subprocess.run(
        [sys.executable, "-c", TELEMETRY_PROBE],
        env=environment,
        capture_output=True,
        encoding="utf-8",
        check=True,
    )
    assert result.stdout == "0 False\n"


class Item(InputSchema):
    """A body with a two-word field."""

    item_name: str


@pytest.mark.usefixtures("database")
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
    assert body["type"] == errors.VALIDATION.uri
    assert {error.get("pointer") or error.get("parameter") for error in body["errors"]} == {
        "/itemName",
        "limit",
    }


@pytest.mark.parametrize(
    "body",
    [
        b'{"a": 1, "a": 2}',
        b'{"a": {"b": 1, "b": 2}}',
        b'{"a": 9007199254740992}',
        b'{"a": 1E400}',
        b'{"a": 3.141592653589793238462643383279}',
        b'{"a": NaN}',
        b'{"a": "\\uDEAD"}',
        b'{"\\uFFFF": 1}',
        b'{"a": "\\uFDD0"}',
        b'"text"',
        '{"a": 1}'.encode("utf-16"),
    ],
)
def test_body_that_is_not_ijson(body: bytes) -> None:
    """Each way of breaking I-JSON is caught."""
    assert ijson.problem(body) is not None


@pytest.mark.parametrize(
    "body",
    [b'{"a": 9007199254740991, "b": 0.1, "c": 1.50, "d": "\\uD800\\uDEAD"}', b"[]", b"{"],
)
def test_body_that_is_ijson_or_not_json(body: bytes) -> None:
    """I-JSON passes, and a body that is not JSON is left to FastAPI."""
    assert ijson.problem(body) is None


@pytest.mark.usefixtures("database")
async def test_repeated_member_is_a_validation_error() -> None:
    """The app answers a member name twice with a 422 on the body."""
    transport = ASGITransport(app=main_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/health",
            content=b'{"itemName": "a", "itemName": "b"}',
            headers={"content-type": "application/json"},
        )
    assert response.status_code == 422
    assert response.headers["content-type"] == errors.PROBLEM_JSON
    assert response.json()["errors"] == [
        {"detail": "Duplicate member name: itemName", "pointer": ""}
    ]


@pytest.mark.usefixtures("database")
@pytest.mark.parametrize("body", [b"{", b'{"itemName": NaN}', '{"a": 1}'.encode("utf-16")])
async def test_body_that_is_not_json_is_a_bad_request(body: bytes) -> None:
    """A body that is not JSON is a 400, not a 422."""
    probe = FastAPI()
    errors.install(probe)
    ijson.install(probe)

    @probe.post("/items")
    async def create_item(item: Item) -> None:
        """Accept an item."""

    transport = ASGITransport(app=probe)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/items", content=body, headers={"content-type": "application/json"}
        )
    assert response.status_code == 400
    assert response.headers["content-type"] == errors.PROBLEM_JSON
    assert response.json()["type"] == "about:blank"


@pytest.mark.parametrize(
    ("minimum", "user_agent"),
    [
        ("1.4.0", "mobile/1.3.9"),
        ("1.10.0", "mobile/1.9.0"),
        ("1.4.0", "mobile/1.4"),
        ("1.4.0", "mobile/abc"),
        ("1.4.0", "mobile"),
    ],
)
async def test_outdated_client_is_rejected(
    monkeypatch: pytest.MonkeyPatch, minimum: str, user_agent: str
) -> None:
    """A version below the minimum, or malformed, is outdated."""
    monkeypatch.setattr(settings, "min_client_versions", {"mobile": minimum})
    transport = ASGITransport(app=main_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health", headers={"User-Agent": user_agent})
    assert response.status_code == 400
    assert response.headers["content-type"] == errors.PROBLEM_JSON
    assert response.json()["type"] == errors.CLIENT_OUTDATED.uri


async def test_problem_types_are_documented() -> None:
    """The URI of each problem type serves its title and status."""
    transport = ASGITransport(app=main_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for problem in errors.TYPES.values():
            response = await client.get(urlsplit(problem.uri).path)
            assert response.status_code == 200
            assert response.headers["content-type"].startswith("text/html")
            assert problem.title in response.text
            assert str(problem.status.value) in response.text


@pytest.mark.usefixtures("database")
async def test_invalid_page_token_points_to_the_parameter() -> None:
    """A bad page token, or one with other filters, is a 422."""
    probe = FastAPI()
    errors.install(probe)
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
