# PostgreSQL y PostGIS

La base de datos.

## Proyecto

Plantilla: [models/base.py](../plantilla/server/src/app/models/base.py), con los tipos, las claves y las columnas espaciales, y [tests/test_conventions.py](../plantilla/server/tests/test_conventions.py), con las pruebas de «Cumplimiento», del servidor de [fastapi.md](fastapi.md).

- PostgreSQL 17 y PostGIS 3.5, los de los paquetes del servidor ([despliegue.md](despliegue.md#máquina)).
- GeoAlchemy2 0.21.0, en el servidor que guarda geografía.

## Nombres

Estándares: [*Data Definition*](../fuentes/postgresql/ddl.sgml) e [*Indexes*](../fuentes/postgresql/indices.sgml) de PostgreSQL.

- Los nombres van en snake_case y sin comillas.
- La clave primaria de una sola columna se llama `id`.
- Una clave foránea se llama `<tabla>_id`, o `<rol>_id` si hay más de una hacia la misma tabla o si apunta a la propia.
- Una columna que guarda una magnitud lleva de sufijo, en minúsculas, la abreviatura oficial de su unidad: `distance_m`, `weight_g`.
- Las columnas `timestamptz` terminan en `_at`.
- Las tablas van en singular ([Data Definition, *Table Basics*](../fuentes/postgresql/ddl.sgml)).
- Un índice que nombra el modelo se llama `ix_<tabla>_<para qué sirve>`, como `ix_event_log_critical` ([Indexes, *Introduction*](../fuentes/postgresql/indices.sgml)).
- El nombre de una tabla no empieza por `pg_` ([Data Definition, *The System Catalog Schema*](../fuentes/postgresql/ddl.sgml)).

## Clave primaria

Estándares: [*Data Definition*](../fuentes/postgresql/ddl.sgml) y [*Data Types*](../fuentes/postgresql/datatype.sgml) de PostgreSQL.

- `text` con un `CHECK` de su formato, en una tabla de valores que codifica un estándar, como los países de ISO 3166-1, con su código como clave: es el mismo en todos los entornos y se lee sin unir tablas.
- `uuid` con `gen_random_uuid()`, en una tabla cuyas filas crea el cliente, que genera el id para crear por `PUT`, como fija [transversal.md](transversal.md#reintentos), o cuyas filas pertenecen a un usuario y no deben poder enumerarse.
- Una tabla particionada lleva como clave su id, de una de estas convenciones, y las columnas de partición, como `(id, created_at)`: PostgreSQL exige que la clave las incluya. [PostgreSQL 17](https://www.postgresql.org/docs/17/ddl-partitioning.html#DDL-PARTITIONING-DECLARATIVE-LIMITATIONS)
- Una tabla cuyas filas se identifican por un par de valores, como `(role, permission)`, lleva ese par como clave, sin id propio. Cada columna es una clave foránea o un `text`.
- Una clave foránea tiene el tipo de la clave a la que apunta.
- `integer` identity, en una lista propia del equipo, igual para todos los usuarios, cuyo tope cabe en `integer` ([Data Types, *Integer Types*](../fuentes/postgresql/datatype.sgml)).
- `bigint` identity, en una tabla cuyas filas crea el propio servidor, como el registro de eventos ([Data Types, *Integer Types*](../fuentes/postgresql/datatype.sgml)).
- Una identity es `GENERATED ALWAYS`, que rechaza un id escrito a mano ([Data Definition, *Identity Columns*](../fuentes/postgresql/ddl.sgml)).
- Toda tabla tiene clave primaria ([Data Definition, *Primary Keys*](../fuentes/postgresql/ddl.sgml)).
- Una fila se identifica por su clave primaria, nunca por `ctid`, que cambia al actualizarla ([Data Definition, *System Columns*](../fuentes/postgresql/ddl.sgml)).

## Esquemas

Estándar: [*Data Definition*](../fuentes/postgresql/ddl.sgml) de PostgreSQL.

- Las extensiones, como PostGIS, van en `public`: la base es de una sola app, y GeoAlchemy2 escribe sus tipos y funciones sin esquema, así que otro esquema tendría que estar en el `search_path` de cada rol.
- Las tablas de la app van en `public`, y solo el dueño de la base crea objetos en él, como en la configuración por defecto de PostgreSQL 17: ningún otro rol cambia a qué objeto apunta una consulta ([Data Definition, *Usage Patterns*](../fuentes/postgresql/ddl.sgml)).

## Geografía

Estándar: [*Data Management*](../fuentes/postgis/using_postgis_dataman.xml) de PostGIS.

- El ORM declara las columnas espaciales con GeoAlchemy2.
- Una columna espacial se declara con `geo_point()` o `geo_line()`, que crean un `Geography` por columna: GeoAlchemy2 copia el `nullable` entre la columna y su tipo, y un `Geography` compartido en un `Annotated` mezcla el de todas las columnas que lo usan. [GeoAlchemy2 0.21.0](https://raw.githubusercontent.com/geoalchemy/geoalchemy2/0.21.0/geoalchemy2/admin/dialects/common.py)
- `GeoPoint` y `GeoLine` son alias de `WKBElement`, solo para `Mapped[...]`.
- `env.py` le pasa a Alembic los `alembic_helpers` de GeoAlchemy2. Sin ellos, la autogeneración crea el índice espacial dos veces y propone borrar `spatial_ref_sys`. [GeoAlchemy2 0.21.0](https://raw.githubusercontent.com/geoalchemy/geoalchemy2/0.21.0/doc/alembic.rst)
- Las columnas espaciales son `geography(<tipo>, 4326)`: el área de cada producto no se conoce de antemano, `geography` mide en metros sin elegir proyección, y 4326 es el WGS 84 del GeoJSON de [transversal.md](transversal.md#mapas) ([PostGIS, *When to use the Geography data type*](../fuentes/postgis/using_postgis_dataman.xml) y [*Geography Data Type*](../fuentes/postgis/using_postgis_dataman.xml)).
- Toda columna espacial lleva un índice GiST, el que crea GeoAlchemy2 con su `spatial_index` por defecto ([PostGIS, *Spatial Indexes*](../fuentes/postgis/using_postgis_dataman.xml) y [*GiST Indexes*](../fuentes/postgis/using_postgis_dataman.xml)).
- Las distancias que recibe o devuelve una función de `geography` van en metros, y las áreas, en metros cuadrados ([PostGIS, *Using Geography Tables*](../fuentes/postgis/using_postgis_dataman.xml)).

## Índices

Estándares: [*Data Definition*](../fuentes/postgresql/ddl.sgml) e [*Indexes*](../fuentes/postgresql/indices.sgml) de PostgreSQL.

- Toda clave foránea encabeza un índice: el de la clave primaria, el de un `UNIQUE` o uno propio. Sin él, borrar una fila del padre o cambiar su clave recorre la tabla hija entera ([Data Definition, *Foreign Keys*](../fuentes/postgresql/ddl.sgml)).
- Un índice es de una sola columna, salvo que una consulta frecuente filtre u ordene por varias. Pasa de tres columnas solo si lo pide una consulta concreta, como la de una lista paginada con sus filtros ([Indexes, *Multicolumn Indexes*](../fuentes/postgresql/indices.sgml) y [*Indexes and ORDER BY*](../fuentes/postgresql/indices.sgml)).
- Un índice que ninguna consulta usa se borra ([Indexes, *Introduction*](../fuentes/postgresql/indices.sgml)).
- Una clave primaria o un `UNIQUE` no llevan otro índice sobre sus mismas columnas: ya crean el suyo ([Indexes, *Unique Indexes*](../fuentes/postgresql/indices.sgml)).
- Nunca se crea un índice parcial por cada valor de una columna: va un solo índice que empieza por ella, o la tabla se particiona ([Indexes, *Partial Indexes*](../fuentes/postgresql/indices.sgml)).
- Una columna que el índice solo devuelve va en `INCLUDE`, nunca como columna de su clave, y solo para un index-only scan de una tabla que cambia poco. Una columna ancha no va en `INCLUDE` ([Indexes, *Index-Only Scans and Covering Indexes*](../fuentes/postgresql/indices.sgml)).

## JSON

Estándar: [*JSON Types*](../fuentes/postgresql/json.sgml) de PostgreSQL.

- Un documento JSON es `jsonb` ([Data Types, *JSON Types*](../fuentes/postgresql/json.sgml)).
- Un documento JSON tiene una estructura predecible, aunque la base no la imponga ([JSON Types, *Designing JSON Documents*](../fuentes/postgresql/json.sgml)).
- Un documento JSON es un dato atómico: un `UPDATE` bloquea la fila entera, y lo que cambia por separado va en su propia columna o tabla ([JSON Types, *Designing JSON Documents*](../fuentes/postgresql/json.sgml)).

## Mantenimiento

Estándar: [*Data Management*](../fuentes/postgis/using_postgis_dataman.xml) de PostGIS.

- La base corre con `autovacuum` activo, su valor por defecto ([PostGIS, *Tuning Index Usage*](../fuentes/postgis/using_postgis_dataman.xml)).

## Particiones

Estándar: [*Data Definition*](../fuentes/postgresql/ddl.sgml) de PostgreSQL.

- Una tabla se particiona con `PARTITION BY`, nunca por herencia ni con vistas `UNION ALL` ([Data Definition, *Table Partitioning*](../fuentes/postgresql/ddl.sgml)).
- Una tabla se particiona solo si se espera que supere la memoria del servidor ([Data Definition, *Table Partitioning*](../fuentes/postgresql/ddl.sgml)).
- La clave de partición es la columna por la que filtra la mayoría de las consultas, y lo que se borra junto, como lo vencido de una retención, cae en una misma partición ([Data Definition, *Best Practices for Declarative Partitioning*](../fuentes/postgresql/ddl.sgml)).

## Restricciones

Estándar: [*Data Definition*](../fuentes/postgresql/ddl.sgml) de PostgreSQL.

- Toda clave foránea declara `ON DELETE`: `CASCADE` si el hijo pertenece al padre, `RESTRICT` si no. Ni `SET NULL` ni `SET DEFAULT`: borrar el padre no cambia en silencio una fila que no le pertenece ([Data Definition, *Foreign Keys*](../fuentes/postgresql/ddl.sgml)).
- Una columna admite `NULL` solo si su dato puede faltar ([Data Definition, *Not-Null Constraints*](../fuentes/postgresql/ddl.sgml)).
- Un `CHECK` mira solo su fila. Una regla entre filas o entre tablas es un `UNIQUE`, un `EXCLUDE` o una clave foránea ([Data Definition, *Check Constraints*](../fuentes/postgresql/ddl.sgml)).
- Un `CHECK` da siempre el mismo resultado para la misma fila: no llama a una función que pueda cambiar ([Data Definition, *Check Constraints*](../fuentes/postgresql/ddl.sgml)).

## Tipos

Estándar: [*Data Types*](../fuentes/postgresql/datatype.sgml) de PostgreSQL.

- Un largo máximo que pida el dominio va en un `CHECK`: la restricción tiene nombre, admite también un mínimo y nunca recorta, como `varchar(n)` al convertir. [PostgreSQL 17](https://www.postgresql.org/docs/17/datatype-character.html)
- Las fechas con hora son `timestamptz`, y no `timestamp`: es el par de las `datetime` aware de [python.md](python.md#fechas), y `timestamp` descarta la zona sin avisar. [PostgreSQL 17](https://www.postgresql.org/docs/17/datatype-datetime.html#DATATYPE-DATETIME-INPUT-TIME-STAMPS)
- Las duraciones son segundos enteros, y no `interval`, que guarda meses y días aparte y no equivale a una cantidad fija de segundos. [PostgreSQL 17](https://www.postgresql.org/docs/17/datatype-datetime.html#DATATYPE-INTERVAL-INPUT)
- Un valor enumerado es `text` con un `CHECK` que lista los valores. Quitar un valor de un `enum` obliga a recrear el tipo; un `CHECK` se reemplaza en una migración. [PostgreSQL 17](https://www.postgresql.org/docs/17/datatype-enum.html#DATATYPE-ENUM-IMPLEMENTATION-DETAILS)
- Un `numeric` va sin precisión ni escala. Con escala declarada, redondea sin avisar lo que la excede. [PostgreSQL 17](https://www.postgresql.org/docs/17/datatype-numeric.html#DATATYPE-NUMERIC-DECIMAL)
- Un monto va junto al código de su moneda, en una columna `text`.
- Las cadenas son `text` ([Data Types, *Character Types*](../fuentes/postgresql/datatype.sgml)).
- Un entero que no es clave primaria es `integer`, o `bigint` si el rango de `integer` no alcanza, y nunca `smallint` ([Data Types, *Integer Types*](../fuentes/postgresql/datatype.sgml)).
- Un monto, o una cantidad que debe ser exacta, es `numeric`, nunca `real`, `double precision` ni `money` ([Data Types, *Arbitrary Precision Numbers*](../fuentes/postgresql/datatype.sgml), [*Floating-Point Types*](../fuentes/postgresql/datatype.sgml) y [*Monetary Types*](../fuentes/postgresql/datatype.sgml)).
- Una dirección IP es `inet`, y una red, `cidr`, nunca `text` ([Data Types, *Network Address Types*](../fuentes/postgresql/datatype.sgml)).
- Una hora con zona va en `timestamptz`: no se usa `time with time zone` ([Data Types, *Date/Time Types*](../fuentes/postgresql/datatype.sgml) y [*Time Zones*](../fuentes/postgresql/datatype.sgml)).
- Una zona horaria se nombra con su nombre de la base IANA, como `America/Mexico_City`, y no con una especificación POSIX ([Data Types, *Time Zones*](../fuentes/postgresql/datatype.sgml)).
- Un valor por defecto, una vista o una función toman la hora con `now()` o `CURRENT_DATE`, nunca con las cadenas `'now'`, `'today'`, `'tomorrow'` ni `'yesterday'`, que quedan fijas al guardarse ([Data Types, *Special Values*](../fuentes/postgresql/datatype.sgml)).
- Una fecha escrita en SQL va en ISO 8601, como `'2026-01-08'` ([Data Types, *Date/Time Input*](../fuentes/postgresql/datatype.sgml)).
- Una constante booleana se escribe `TRUE` o `FALSE` ([Data Types, *Boolean Type*](../fuentes/postgresql/datatype.sgml)).
- Un `bytea` escrito en SQL va en hexadecimal, `'\x…'`, y no en el formato de escape ([Data Types, *bytea Hex Format*](../fuentes/postgresql/datatype.sgml) y [*bytea Escape Format*](../fuentes/postgresql/datatype.sgml)).

## Cumplimiento

Las pruebas son las de `tests/test_conventions.py` de [fastapi.md](fastapi.md).

| Convención | Herramienta |
| :--- | :--- |
| GeoAlchemy2 0.21.0 | [scripts/verificar.py](../scripts/verificar.py) |
| Toda tabla tiene clave primaria | `test_primary_key_is_allowed` y `test_primary_key_rules` |
| Clave `text` con `CHECK`, identity `integer` o `bigint` `ALWAYS` o `uuid` con `gen_random_uuid()`, la de una tabla particionada y la de un par de valores | `test_primary_key_is_allowed` y `test_primary_key_rules` |
| Una clave foránea tiene el tipo de la clave a la que apunta | `test_foreign_keys_match_key_type` y `test_foreign_key_type_mismatch` |
| Cadenas `text` | `test_strings_are_text` |
| `timestamptz` | `test_datetimes_are_aware` |
| Duraciones sin `interval` | `test_durations_are_seconds` |
| `numeric` sin precisión ni escala | `test_numerics_are_unscaled` |
| Enumerados como `text` con `CHECK` | `test_enums_are_checked_text` |
| Columnas espaciales `geography` en 4326, con el índice de `spatial_index` | `test_geography_columns` |
| `ON DELETE` `CASCADE` o `RESTRICT` en toda clave foránea | `test_foreign_keys_declare_on_delete` |
| Toda clave foránea encabeza un índice | `test_foreign_keys_are_indexed` y `test_unindexed_key` |
