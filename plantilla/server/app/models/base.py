from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from importlib.util import find_spec
from typing import Annotated, Any
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import BOOLEAN, BYTEA, DATE, DOUBLE_PRECISION, INTEGER, JSONB, TEXT, TIME, TIMESTAMP, NUMERIC, BIGINT, SMALLINT, UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, MappedColumn, mapped_column


class Base(DeclarativeBase):
    # --- Type Annotation Map ---
    type_annotation_map = {
        bool: BOOLEAN,
        bytes: BYTEA,
        date: DATE,
        datetime: TIMESTAMP(timezone=True),
        dict: JSONB,
        float: DOUBLE_PRECISION,
        int: INTEGER,
        list: JSONB,
        str: TEXT,
        time: TIME,
        UUID: PG_UUID(as_uuid=True),
    }

# --- Annotated Types (Pure PostgreSQL) ---
Money = Annotated[Decimal, mapped_column(NUMERIC(8, 2), server_default="0.00")]
Percent = Annotated[Decimal, mapped_column(NUMERIC(5, 2), server_default="0.00")]

PkUuid = Annotated[UUID, mapped_column(primary_key=True, server_default=sa.func.gen_random_uuid())]
PkBigint = Annotated[int, mapped_column(BIGINT, primary_key=True, autoincrement=True)]
PkInt = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
PkSmallint = Annotated[int, mapped_column(SMALLINT, primary_key=True, autoincrement=True)]

IsActive = Annotated[bool, mapped_column(server_default=sa.true())]
CreatedAt = Annotated[datetime, mapped_column(server_default=sa.func.now())]
UpdatedAt = Annotated[datetime | None, mapped_column(server_default=sa.func.now(), onupdate=sa.func.now())]


if find_spec("geoalchemy2") is not None:
    from geoalchemy2 import Geography, WKBElement

    # GeoPoint/GeoLine son alias de tipo puros, para la anotación `Mapped[...]`. La columna se
    # declara con geo_point()/geo_line().
    #
    # NO son `Annotated[..., mapped_column(Geography(...))]`, como sí lo son el resto de los
    # alias de este archivo, y la diferencia importa: geoalchemy2 guarda `nullable` **en la
    # instancia del tipo** y la muta al crear cada columna. Un Annotated comparte una única
    # instancia de `Geography` entre todas las columnas que lo usan, así que la última columna
    # procesada le impone su `nullable` a todas las demás — en silencio, y solo se nota al
    # generar la migración. Una instancia nueva por columna elimina el acoplamiento.
    GeoPoint = WKBElement
    GeoLine = WKBElement

    def geo_point(*, nullable: bool = False, **kwargs: Any) -> MappedColumn[Any]:
        return mapped_column(
            Geography(geometry_type="POINT", srid=4326, spatial_index=False, nullable=nullable),
            nullable=nullable,
            **kwargs,
        )

    def geo_line(*, nullable: bool = False, **kwargs: Any) -> MappedColumn[Any]:
        return mapped_column(
            Geography(geometry_type="LINESTRING", srid=4326, spatial_index=False, nullable=nullable),
            nullable=nullable,
            **kwargs,
        )


def StringEnumType(enum_cls: type[Enum]) -> sa.Enum:
    """Enum guardado como VARCHAR + CHECK, en vez de un tipo ENUM nativo de PostgreSQL.

    `create_constraint=True` es explícito y NO es el default: desde SQLAlchemy 1.4 vale `False`,
    con lo cual `native_enum=False` produce un VARCHAR pelado y la base acepta cualquier cadena.
    `validate_strings=True` solo valida del lado de Python, así que sin el CHECK la única
    protección desaparece en cuanto algo escribe por fuera del ORM (SQL directo, una carga
    masiva, un job de mantenimiento).

    Importa especialmente aquí porque hay enums que gobiernan comportamiento legal o financiero
    —`account_type` decide el cruce de discover, `RelationshipType` tiene implicación de
    cumplimiento, los `status` de pagos y moderación—: un valor mal escrito no rompe nada de
    forma visible, simplemente deja de coincidir con los filtros que lo buscan.

    Contrapartida aceptada: agregar un valor al enum pasa a requerir una migración que recree el
    CHECK. Es deseable — en este dominio, cambiar el conjunto de valores permitidos ES un cambio
    de esquema y conviene que se note.
    """
    return sa.Enum(
        enum_cls,
        native_enum=False,
        create_constraint=True,
        values_callable=lambda enum: [member.value for member in enum],
        validate_strings=True,
    )
