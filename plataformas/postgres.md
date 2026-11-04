# PostgreSQL y PostGIS

La base de datos.

## Nombres

Estándar: la entrada *Identifiers and Key Words* de
[*SQL Syntax*](../fuentes/postgresql/syntax.sgml) de PostgreSQL.

- Los nombres van en snake_case y sin comillas, las tablas en singular y las claves foráneas como
  `<tabla>_id`.
- Una columna que guarda una magnitud lleva de sufijo el símbolo del SI de su unidad:
  `distance_m`, `weight_g`. El nombre dice en qué unidad está el valor.
- Las duraciones son segundos enteros, `_s`, y no `interval`. Todos los clientes leen un entero, y
  Dart no trae con qué leer la duración ISO 8601 en que Pydantic serializa un `timedelta`.

## Clave primaria

Estándares: de PostgreSQL 17, la versión de Debian 13, las entradas de los tipos numéricos y de
`uuid` de [*Data Types*](../fuentes/postgresql/datatype.sgml), la sección *Identity Columns* de
[*Data Definition*](../fuentes/postgresql/ddl.sgml) y la entrada de `gen_random_uuid()` de las
[funciones de UUID](../fuentes/postgresql/func.sgml).

- `text` con un `CHECK` de su formato: en una tabla de valores que codifica un estándar, como los
  países de ISO 3166-1, con su código como clave. Es el mismo en todos los entornos y se lee sin
  unir tablas.
- `smallint` identity: en una lista propia del equipo, igual para todos los usuarios, cuyo tope
  cabe en `smallint`.
- `bigint` identity: en una lista propia del equipo cuyo tope no cabe en `smallint`.
- `uuid` con `gen_random_uuid()`: en una tabla cuyas filas crea el cliente, que genera el id para
  crear por `PUT`, como fija [transversal.md](transversal.md#reintentos), o cuyas filas pertenecen a un usuario y no
  deben poder enumerarse.
- Una tabla particionada lleva como clave su id, de una de las reglas anteriores, y las columnas de
  partición, como `(id, created_at)`: PostgreSQL exige que la clave las incluya.
- Una tabla cuyas filas se identifican por un par de valores, como `(role, permission)`, lleva ese
  par como clave, sin id propio. Cada columna es una clave foránea o un `text`.
- Una identity es `GENERATED ALWAYS`, que rechaza un id escrito a mano.
- Una clave foránea tiene el tipo de la clave que apunta.

## Definición de datos

Estándar: [*Data Definition*](../fuentes/postgresql/ddl.sgml) de PostgreSQL, salvo *Identity
Columns*, que rige en «Clave primaria», y el párrafo de *Foreign Keys* sobre indexar las columnas
que referencian, que rige en «Índices».

- Toda clave foránea declara `ON DELETE`: `CASCADE` si el hijo pertenece al padre, `RESTRICT` si
  no. Qué pasa al borrar queda escrito en el modelo.

## Geografía

Estándar: [*Data Management*](../fuentes/postgis/using_postgis_dataman.xml) de PostGIS, entero.

- Las columnas espaciales son `geography(<tipo>, 4326)`. El área de cada producto no se conoce de
  antemano, y `geography` mide en metros sin elegir proyección.
- El ORM las declara con GeoAlchemy2.
- La columna se declara con `geo_point()` o `geo_line()`, que crean un `Geography` por columna: un
  `Geography` compartido en un `Annotated` le impone su `nullable` a todas las columnas que lo usan.
- `GeoPoint` y `GeoLine` son alias de `WKBElement`, solo para `Mapped[...]`.
- La columna lleva `spatial_index=False`, y su índice GiST lo crea la migración, como los demás
  índices.

## Índices

Estándares: [*Indexes*](../fuentes/postgresql/indices.sgml), entero, y el párrafo de *Foreign Keys*
de [*Data Definition*](../fuentes/postgresql/ddl.sgml) sobre indexar las columnas que referencian,
de PostgreSQL.

- Toda clave foránea lleva índice. Endurece *Data Definition*, que lo da por buena idea y no lo crea:
  sin él, borrar el padre o unir las tablas recorre la tabla hija entera.

## Tipos

Estándares: las entradas de [*Data Types*](../fuentes/postgresql/datatype.sgml) de los tipos que
nombra esta sección, salvo los de «Clave primaria», y
[*JSON Types*](../fuentes/postgresql/json.sgml), entero, de PostgreSQL.

- Las cadenas son `text`. Un largo máximo que pida el dominio va en un `CHECK`: la restricción
  tiene nombre, admite también un mínimo y nunca recorta, como `varchar(n)` al convertir.
- Las fechas con hora son `timestamptz`, y no `timestamp`: es el par de las `datetime` aware de
  [python.md](python.md), y `timestamp` descartaría la zona sin avisar.
- Un valor enumerado es `text` con un `CHECK` que lista los valores. Quitar un valor de un `enum`
  obliga a recrear el tipo; un `CHECK` se reemplaza en una migración.
- Un monto es `numeric` sin precisión ni escala, junto al código de su moneda en `text`. Con escala
  declarada, `numeric` redondea sin avisar lo que la excede.

## Cumplimiento

Con las pruebas de `tests/test_conventions.py` de [fastapi.md](fastapi.md):

| Convención | Herramienta |
|---|---|
| Clave `text`, identity `ALWAYS` o `uuid` con `gen_random_uuid()`, la de una tabla particionada y la de un par de valores | `test_primary_key_is_allowed` y `test_primary_key_rules` |
| Cadenas `text` | `test_strings_are_text` |
| `timestamptz` | `test_datetimes_are_aware` |
| Enumerados como `text` con `CHECK` | `test_enums_are_checked_text` |
| `ON DELETE` en toda clave foránea | `test_foreign_keys_declare_on_delete` |
| Índice en toda clave foránea | `test_foreign_keys_are_indexed` |
