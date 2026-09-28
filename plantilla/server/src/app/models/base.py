"""The declarative base: PostgreSQL types and constraint names."""

from datetime import datetime
from enum import StrEnum
from typing import Annotated, Any
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, TEXT, TIMESTAMP
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import DeclarativeBase, mapped_column

# The convention of the Alembic documentation.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


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
            values_callable=lambda members: [member.value for member in members],
        ),
    }


UuidPk = Annotated[UUID, mapped_column(primary_key=True, server_default=sa.text("uuidv7()"))]


@compiles(sa.Enum, "postgresql")
def compile_enum(type_: sa.Enum, compiler: Any, **kw: Any) -> str:
    """Store a non-native enum as text, like every other string."""
    if type_.native_enum:
        return str(compiler.visit_enum(type_, **kw))
    return "TEXT"
