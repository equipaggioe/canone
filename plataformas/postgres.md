# PostgreSQL y PostGIS

La base de datos.

## Nombres

Estándar: [*SQL Syntax*](../estandares/postgresql/syntax.sgml) de PostgreSQL.

- Los nombres van en snake_case y sin comillas, las tablas en singular y las claves foráneas como
  `<tabla>_id`.
- Una columna que guarda una magnitud lleva de sufijo el símbolo del SI de su unidad:
  `distance_m`, `weight_g`. El nombre dice en qué unidad está el valor.
- Las duraciones son segundos enteros, `_s`, y no `interval`. Todos los clientes leen un entero, y
  Dart no trae con qué leer la duración ISO 8601 en que Pydantic serializa un `timedelta`.

## Clave primaria

Estándares: [*Data Types*](../estandares/postgresql/datatype.sgml),
[*Identity Columns*](../estandares/postgresql/ddl.sgml) y las
[funciones de UUID](../estandares/postgresql/func.sgml) de PostgreSQL 17, la versión de Debian 13.

- `text` con un `CHECK` de su formato: en una tabla de valores que codifica un estándar, como los
  países de ISO 3166-1, con su código como clave. Es el mismo en todos los entornos y se lee sin
  unir tablas.
- `smallint` identity: en una lista propia del equipo, igual para todos los usuarios, cuyo tope
  cabe en `smallint`.
- `bigint` identity: en una lista propia del equipo cuyo tope no cabe en `smallint`.
- `uuid` con `gen_random_uuid()`: en una tabla cuyas filas crea el cliente, que genera el id para
  crear por `PUT`, como fija [fastapi.md](fastapi.md), o cuyas filas pertenecen a un usuario y no
  deben poder enumerarse.
- Una identity es `GENERATED ALWAYS`, que rechaza un id escrito a mano.
- Una clave foránea tiene el tipo de la clave que apunta.

## Definición de datos

Estándar: [*Data Definition*](../estandares/postgresql/ddl.sgml) de PostgreSQL.

- Toda clave foránea declara `ON DELETE`: `CASCADE` si el hijo pertenece al padre, `RESTRICT` si
  no. Qué pasa al borrar queda escrito en el modelo.
- Las filas se borran de verdad, sin columna de borrado lógico. Un borrado lógico obliga a filtrar
  cada consulta y cada índice único.

## Geografía

Estándar: [*Data Management*](../estandares/postgis/using_postgis_dataman.xml) de PostGIS.

- Las columnas espaciales son `geography(<tipo>, 4326)`. El área de cada producto no se conoce de
  antemano, y `geography` mide en metros sin elegir proyección.
- El ORM las declara con GeoAlchemy2.

## Índices

Estándares: [*Indexes*](../estandares/postgresql/indices.sgml) y
[*Data Definition*](../estandares/postgresql/ddl.sgml) de PostgreSQL.

- Toda clave foránea lleva índice. Endurece *Data Definition*, que lo da por buena idea y no lo crea:
  sin él, borrar el padre o unir las tablas recorre la tabla hija entera.

## Tipos

Estándares: [*Data Types*](../estandares/postgresql/datatype.sgml) y
[*JSON Types*](../estandares/postgresql/json.sgml) de PostgreSQL, y la
[lista de monedas](../estandares/iso/iso-4217-list-one.xml) de ISO 4217.

- Las cadenas son `text`. Un largo máximo que pida el dominio va en un `CHECK`: la restricción
  tiene nombre, admite también un mínimo y nunca recorta, como `varchar(n)` al convertir.
- Las fechas con hora son `timestamptz`, y no `timestamp`: es el par de las `datetime` aware de
  [python.md](python.md), y `timestamp` descartaría la zona sin avisar.
- Un valor enumerado es `text` con un `CHECK` que lista los valores. Quitar un valor de un `enum`
  obliga a recrear el tipo; un `CHECK` se reemplaza en una migración.
- Un monto es `numeric` sin precisión ni escala, junto al código de su moneda en `text`. Con escala
  declarada, `numeric` redondea sin avisar lo que la excede.

## Cómo se hace cumplir

Con las pruebas de `tests/test_conventions.py` de [fastapi.md](fastapi.md):

| Qué | Prueba |
|---|---|
| Clave `text`, identity `ALWAYS` o `uuid` con `gen_random_uuid()` | `test_primary_key_is_allowed` |
| Cadenas `text` | `test_strings_are_text` |
| `timestamptz` | `test_datetimes_are_aware` |
| Enumerados como `text` con `CHECK` | `test_enums_are_checked_text` |
| `ON DELETE` en toda clave foránea | `test_foreign_keys_declare_on_delete` |
| Índice en toda clave foránea | `test_foreign_keys_are_indexed` |
