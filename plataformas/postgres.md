# PostgreSQL y PostGIS

La base de datos.

## Tipos

Estándares: [*Data Types*](../estandares/postgresql/datatype.sgml),
[*JSON Types*](../estandares/postgresql/json.sgml) y las
[funciones](../estandares/postgresql/func.sgml) de PostgreSQL 17, la versión de Debian 13.

- La clave primaria es un `uuid` generado con `gen_random_uuid()`, la versión 4 que la
  documentación da por apropiada para la mayoría de las aplicaciones. El cliente genera el ID para
  crear por `PUT`, como fija [fastapi.md](fastapi.md), y un entero secuencial solo lo genera la base,
  revela cuántos hay y se adivina en una URL.
- Las cadenas son `text`. Un largo máximo que pida el dominio va en un `CHECK`: la restricción
  tiene nombre, admite también un mínimo y nunca recorta, como `varchar(n)` al convertir.
- Las fechas con hora son `timestamptz`, y no `timestamp`: es el par de las `datetime` aware de
  [python.md](python.md), y `timestamp` descartaría la zona sin avisar.
- Un valor enumerado es `text` con un `CHECK` que lista los valores. Quitar un valor de un `enum`
  obliga a recrear el tipo; un `CHECK` se reemplaza en una migración.

## Definición de datos

Estándar: [*Data Definition*](../estandares/postgresql/ddl.sgml) de PostgreSQL.

- Toda clave foránea declara `ON DELETE`: `CASCADE` si el hijo pertenece al padre, `RESTRICT` si
  no. Qué pasa al borrar queda escrito en el modelo.
- Las filas se borran de verdad, sin columna de borrado lógico. Un borrado lógico obliga a filtrar
  cada consulta y cada índice único.

## Nombres

Estándar: [*SQL Syntax*](../estandares/postgresql/syntax.sgml) de PostgreSQL.

- Los nombres van en snake_case y sin comillas, las tablas en singular y las claves foráneas como
  `<tabla>_id`.
- Una columna que guarda una magnitud lleva de sufijo el símbolo del SI de su unidad:
  `distance_m`, `weight_g`. El nombre dice en qué unidad está el valor.
- Las duraciones son segundos enteros, `_s`, y no `interval`. Todos los clientes leen un entero, y
  Dart no trae con qué leer la duración ISO 8601 en que Pydantic serializa un `timedelta`.

## Índices

Estándares: [*Indexes*](../estandares/postgresql/indices.sgml) y
[*Data Definition*](../estandares/postgresql/ddl.sgml) de PostgreSQL.

- Toda clave foránea lleva índice. Endurece *Data Definition*, que lo da por buena idea y no lo crea:
  sin él, borrar el padre o unir las tablas recorre la tabla hija entera.

## Geografía

Estándar: [*Data Management*](../estandares/postgis/using_postgis_dataman.xml) de PostGIS.

- Las columnas espaciales son `geography(<tipo>, 4326)`. El área de cada producto no se conoce de
  antemano, y `geography` mide en metros sin elegir proyección.
- El ORM las declara con GeoAlchemy2.

## Cómo se hace cumplir

Con las pruebas de `tests/test_conventions.py` de [fastapi.md](fastapi.md):

| Qué | Prueba |
|---|---|
| Clave `uuid` con `gen_random_uuid()` | `test_primary_key_is_random_uuid` |
| Cadenas `text` | `test_strings_are_text` |
| `timestamptz` | `test_datetimes_are_aware` |
| Enumerados como `text` con `CHECK` | `test_enums_are_checked_text` |
| `ON DELETE` en toda clave foránea | `test_foreign_keys_declare_on_delete` |
| Índice en toda clave foránea | `test_foreign_keys_are_indexed` |
