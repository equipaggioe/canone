# PostgreSQL y PostGIS

La base de datos.

## Proyecto

- PostgreSQL 17 y PostGIS 3.5, los de Debian 13.
- GeoAlchemy2 0.21.0, en el servidor que guarda geografía.

## Nombres

Estándar: la sección *The System Catalog Schema* de [*Data Definition*](../fuentes/postgresql/ddl.sgml) de PostgreSQL.

- Los nombres van en snake_case y sin comillas, y las tablas en singular.
- La clave primaria de una sola columna se llama `id`.
- Las claves foráneas son `<tabla>_id`, o `<rol>_id` si hay más de una hacia la misma tabla o apunta a la propia.
- Una columna que guarda una magnitud lleva de sufijo, en minúsculas, la abreviatura oficial de su unidad: `distance_m`, `weight_g`.
- Las columnas `timestamptz` terminan en `_at`.

## Clave primaria

Estándar: las secciones *Primary Keys* y *System Columns* de [*Data Definition*](../fuentes/postgresql/ddl.sgml) de PostgreSQL.

- `text` con un `CHECK` de su formato: en una tabla de valores que codifica un estándar, como los países de ISO 3166-1, con su código como clave. Es el mismo en todos los entornos y se lee sin unir tablas.
- `integer` identity: en una lista propia del equipo, igual para todos los usuarios, cuyo tope cabe en `integer`.
- `bigint` identity: en una tabla cuyas filas crea el propio servidor, como el registro de eventos.
- `uuid` con `gen_random_uuid()`: en una tabla cuyas filas crea el cliente, que genera el id para crear por `PUT`, como fija [transversal.md](transversal.md#reintentos), o cuyas filas pertenecen a un usuario y no deben poder enumerarse.
- Una tabla particionada lleva como clave su id, de una de las convenciones anteriores, y las columnas de partición, como `(id, created_at)`: PostgreSQL exige que la clave las incluya.
- Una tabla cuyas filas se identifican por un par de valores, como `(role, permission)`, lleva ese par como clave, sin id propio. Cada columna es una clave foránea o un `text`.
- Una identity es `GENERATED ALWAYS`, que rechaza un id escrito a mano.
- Una clave foránea tiene el tipo de la clave que apunta.

## Definición de datos

Estándar: las secciones *Check Constraints*, *Not-Null Constraints*, *Foreign Keys* y *Modifying Tables* de [*Data Definition*](../fuentes/postgresql/ddl.sgml) de PostgreSQL, salvo el párrafo de *Foreign Keys* sobre indexar las columnas que referencian, que rige en «Índices».

- Toda clave foránea declara `ON DELETE`: `CASCADE` si el hijo pertenece al padre, `RESTRICT` si no. Qué pasa al borrar queda escrito en el modelo. Ni `SET NULL` ni `SET DEFAULT`: borrar el padre no cambia en silencio una fila que no le pertenece.

## Geografía

Estándar: las secciones *Geography Data Type* y *GiST Indexes* de [*Data Management*](../fuentes/postgis/using_postgis_dataman.xml) de PostGIS.

- Las columnas espaciales son `geography(<tipo>, 4326)`. El área de cada producto no se conoce de antemano, y `geography` mide en metros sin elegir proyección.
- El ORM las declara con GeoAlchemy2.
- La columna se declara con `geo_point()` o `geo_line()`, que crean un `Geography` por columna: un `Geography` compartido en un `Annotated` le impone su `nullable` a todas las columnas que lo usan.
- `GeoPoint` y `GeoLine` son alias de `WKBElement`, solo para `Mapped[...]`.
- La columna lleva el índice GiST que crea GeoAlchemy2, con el `spatial_index` por defecto, y `env.py` le pasa a Alembic los `alembic_helpers` de GeoAlchemy2. Sin ellos, la autogeneración crea el índice dos veces y propone borrar `spatial_ref_sys`.

## Índices

Estándares: las secciones *Introduction*, *Multicolumn Indexes*, *Unique Indexes*, *Partial Indexes* e *Index-Only Scans and Covering Indexes* de [*Indexes*](../fuentes/postgresql/indices.sgml), y el párrafo de *Foreign Keys* de [*Data Definition*](../fuentes/postgresql/ddl.sgml) sobre indexar las columnas que referencian, de PostgreSQL.

- Toda clave foránea lleva un índice cuyas primeras columnas son las suyas. Sin él, borrar una fila del padre o cambiar su clave recorre la tabla hija entera.

## Tipos

Estándares: las entradas *Character Types*, *Date/Time Types*, *Integer Types*, *Arbitrary Precision Numbers* y *Network Address Types* de [*Data Types*](../fuentes/postgresql/datatype.sgml) y [*JSON Types*](../fuentes/postgresql/json.sgml), entero, de PostgreSQL.

- Las cadenas son `text`. Un largo máximo que pida el dominio va en un `CHECK`: la restricción tiene nombre, admite también un mínimo y nunca recorta, como `varchar(n)` al convertir.
- Las fechas con hora son `timestamptz`, y no `timestamp`: es el par de las `datetime` aware de [python.md](python.md), y `timestamp` descartaría la zona sin avisar.
- Las duraciones son segundos enteros, y no `interval`, que guarda meses y días aparte y no equivale a una cantidad fija de segundos.
- Un valor enumerado es `text` con un `CHECK` que lista los valores. Quitar un valor de un `enum` obliga a recrear el tipo; un `CHECK` se reemplaza en una migración.
- Un `numeric` va sin precisión ni escala. Con escala declarada, redondea sin avisar lo que la excede.
- Un monto es `numeric`, junto al código de su moneda en `text`.

## Cumplimiento

Con las pruebas de `tests/test_conventions.py` de [fastapi.md](fastapi.md):

| Convención | Herramienta |
| :--- | :--- |
| Clave `text` con `CHECK`, identity `integer` o `bigint` `ALWAYS` o `uuid` con `gen_random_uuid()`, la de una tabla particionada y la de un par de valores | `test_primary_key_is_allowed` y `test_primary_key_rules` |
| Una clave foránea tiene el tipo de la clave que apunta | `test_foreign_keys_match_key_type` y `test_foreign_key_type_mismatch` |
| Cadenas `text` | `test_strings_are_text` |
| `timestamptz` | `test_datetimes_are_aware` |
| Duraciones sin `interval` | `test_durations_are_seconds` |
| `numeric` sin precisión ni escala | `test_numerics_are_unscaled` |
| Enumerados como `text` con `CHECK` | `test_enums_are_checked_text` |
| Columnas espaciales `geography` en 4326, con el índice de `spatial_index` | `test_geography_columns` |
| `ON DELETE` `CASCADE` o `RESTRICT` en toda clave foránea | `test_foreign_keys_declare_on_delete` |
| Toda clave foránea encabeza un índice | `test_foreign_keys_are_indexed` y `test_unindexed_key` |
