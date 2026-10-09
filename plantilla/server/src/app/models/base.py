"""The declarative base: PostgreSQL types and constraint names."""

from datetime import datetime
from enum import StrEnum
from importlib.util import find_spec
from typing import Annotated, Any
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, TEXT, TIMESTAMP
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import DeclarativeBase, MappedColumn, mapped_column

# The convention of the Alembic documentation.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


def enum_values(members: type[StrEnum]) -> list[str]:
    """Store each member of a StrEnum by its value."""
    return [member.value for member in members]


class Base(DeclarativeBase):
    """Every table inherits from this one."""

    metadata = sa.MetaData(naming_convention=NAMING_CONVENTION)
    type_annotation_map = {
        str: TEXT,
        datetime: TIMESTAMP(timezone=True),
        dict[str, Any]: JSONB,
        StrEnum: sa.Enum(
            StrEnum,
            native_enum=False,
            create_constraint=True,
            length=None,
            values_callable=enum_values,
        ),
    }


UuidPk = Annotated[UUID, mapped_column(primary_key=True, server_default=sa.text("gen_random_uuid()"))]
SmallIntPk = Annotated[int, mapped_column(sa.SmallInteger, sa.Identity(always=True), primary_key=True)]
BigIntPk = Annotated[int, mapped_column(sa.BigInteger, sa.Identity(always=True), primary_key=True)]

# Only the servers that declare geoalchemy2 store geography; the
# others keep this file unedited.
if find_spec("geoalchemy2") is not None:
    from geoalchemy2 import Geography, WKBElement

    GeoPoint = WKBElement
    GeoLine = WKBElement

    # ADR-0004: a Geography shared through an Annotated takes the
    # nullable of the last column that uses it, so each column builds
    # its own.
    def geo_point(*, nullable: bool) -> MappedColumn[Any]:
        """Declare a point in WGS 84.

        Its GiST index goes in the migration.
        """
        return mapped_column(Geography("POINT", srid=4326, spatial_index=False), nullable=nullable)

    def geo_line(*, nullable: bool) -> MappedColumn[Any]:
        """Declare a line in WGS 84.

        Its GiST index goes in the migration.
        """
        return mapped_column(Geography("LINESTRING", srid=4326, spatial_index=False), nullable=nullable)


@compiles(sa.Enum, "postgresql")
def compile_enum(type_: sa.Enum, compiler: Any, **kw: Any) -> str:
    """Store a non-native enum as text, like every other string."""
    if type_.native_enum:
        return str(compiler.visit_enum(type_, **kw))
    return "TEXT"
