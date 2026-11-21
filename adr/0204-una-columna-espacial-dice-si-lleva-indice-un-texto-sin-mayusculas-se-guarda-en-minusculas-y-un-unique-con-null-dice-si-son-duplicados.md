# ADR-0204 · Una columna espacial dice si lleva índice, un texto sin mayúsculas se guarda en minúsculas, y un `UNIQUE` con `NULL` dice si son duplicados

- **Estado:** Aceptada. El usuario pidió escribir las tres opciones recomendadas (2026-11-20)
- **Fecha:** 2026-11-20
- **Alcance:** «Restricciones» de [plataformas/postgres.md](../plataformas/postgres.md), «Base de datos» de [plataformas/fastapi.md](../plataformas/fastapi.md) y `plantilla/server/src/app/models/base.py`

## Contexto

El [ADR-0203](0203-una-tabla-que-amplia-otra-lleva-su-clave-foranea-como-clave-una-lista-que-se-busca-va-en-una-tabla-y-el-ci-de-canone-prueba-la-plantilla-del-servidor.md) dejó de exigir el índice GiST en toda columna espacial, pero `geo_point()` y `geo_line()` lo creaban siempre.

En los productos:

- comande, equipaggio y raccolta guardan el correo en minúsculas con `CHECK (email = lower(email))`.
- comande y cadenza usan `NULLS NOT DISTINCT` en un `UNIQUE` con una columna que admite `NULL`.

Lo que dice PostgreSQL 17:

- [citext](https://raw.githubusercontent.com/postgres/postgres/REL_17_STABLE/doc/src/sgml/citext.sgml): «Consider using nondeterministic collations instead of this module».
- [Collation Support](https://raw.githubusercontent.com/postgres/postgres/REL_17_STABLE/doc/src/sgml/charset.sgml): una collation no determinista tiene un costo de rendimiento, el B-tree no deduplica, y «certain operations are not possible with nondeterministic collations, such as pattern matching operations. Therefore, they should be used only in cases where they are specifically wanted».
- [Data Definition, *Unique Constraints*](../fuentes/postgresql/ddl.sgml): por defecto dos `NULL` no son iguales, y `NULLS NOT DISTINCT` lo cambia.

Comprobado en Debian 13 con PostgreSQL 17.12, SQLAlchemy 2.1.9, Alembic 1.20.1 y GeoAlchemy2 0.21.0:

| Prueba | Resultado |
| :--- | :--- |
| `CHECK (email = lower(email))` | `'Ana@x.mx'` da `CheckViolation`; `LIKE 'ana%'` encuentra la fila |
| `UNIQUE (tenant, location, key)` con `location` en `NULL` | Entran dos filas iguales |
| `UNIQUE NULLS NOT DISTINCT (…)` | La segunda fila da `duplicate key` |
| Alembic con `postgresql_nulls_not_distinct=True` | La autogeneración lo escribe, y `alembic check` ve que se agregue o se quite |
| `geo_point(nullable=…, spatial_index=…)` | Cada columna guarda su `nullable` y su `spatial_index`; sin `spatial_index`, `TypeError` |

## Decisión

1. **`geo_point()` y `geo_line()` piden `spatial_index`, sin valor por defecto**, como `nullable`: una columna lleva el índice GiST si alguna consulta la busca por su geometría.
2. **Un texto que se compara sin distinguir mayúsculas se guarda en minúsculas**, con un `CHECK` `x = lower(x)`.
3. **Un `UNIQUE` sobre columnas que admiten `NULL` lleva `NULLS NOT DISTINCT`** si dos filas con `NULL` en ellas son duplicadas: elección de *Unique Constraints*.

## Consecuencias

- Cada llamada a `geo_point()` y `geo_line()` de los productos agrega `spatial_index`.
- Un texto en minúsculas admite `LIKE` y la deduplicación del B-tree; una mayúscula que llega sin normalizar falla al insertar.
- Si el correo se compara sin mayúsculas lo decide [autenticacion.md](../plataformas/autenticacion.md), que hoy no lo dice.

## Descartado

- **`spatial_index` con `True` por defecto:** es un valor por defecto silencioso.
- **Collation no determinista:** en PostgreSQL 17 no admite `LIKE` y cuesta rendimiento.
- **`citext`:** PostgreSQL recomienda la collation no determinista en su lugar.
- **Índice único sobre `lower(x)`:** cada consulta tiene que acordarse de `lower()`.
- **Dos índices únicos parciales:** más objetos para lo mismo.
- **Un centinela en vez de `NULL`:** contradice que una columna admite `NULL` solo si su dato puede faltar.
