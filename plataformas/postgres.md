# PostgreSQL y PostGIS

La base de datos.

## Tipos

Estándar: [*Data Types*](../estandares/postgresql/datatype.sgml) de PostgreSQL.

- La clave primaria es un `uuid` generado con `uuidv7()`. Los IDs viajan en URLs y clientes, y un
  entero secuencial revela cuántos hay y se adivina; la versión 7 va ordenada por tiempo, así que
  el índice crece al final.
- Las cadenas son `text`. Un largo máximo que pida el dominio va en un `CHECK`.
- Las fechas con hora son `timestamptz`. Endurece la recomendación de la documentación: es el par
  de las `datetime` aware de [python.md](python.md), y `timestamp` descartaría la zona sin avisar.
- Un valor enumerado es `text` con un `CHECK` que lista los valores. Quitar un valor de un `enum`
  obliga a recrear el tipo; un `CHECK` se reemplaza en una migración.
- El JSON es `jsonb`. Se indexa y se consulta por clave.

## Definición de datos

Estándar: [*Data Definition*](../estandares/postgresql/ddl.sgml) de PostgreSQL.

- Toda clave foránea declara `ON DELETE`: `CASCADE` si el hijo pertenece al padre, `RESTRICT` si
  no. Qué pasa al borrar queda escrito en el modelo.
- Las filas se borran de verdad, sin columna de borrado lógico. Un borrado lógico obliga a filtrar
  cada consulta y cada índice único.

## Nombres

Estándar: [*SQL Syntax*](../estandares/postgresql/syntax.sgml) de PostgreSQL.

- Los nombres van en snake_case y sin comillas, las tablas en plural y las claves foráneas como
  `<singular>_id`.

## Índices

Estándar: [*Indexes*](../estandares/postgresql/indices.sgml) de PostgreSQL.

- Toda clave foránea lleva índice. Endurece la documentación, que solo avisa que PostgreSQL no lo
  crea: sin él, borrar el padre o unir las tablas recorre la tabla hija entera.

## Geografía

Estándar: [*Data Management*](../estandares/postgis/using_postgis_dataman.xml) de PostGIS.

- Las columnas espaciales son `geography(<tipo>, 4326)`. El área de cada producto no se conoce de
  antemano, y `geography` mide en metros sin elegir proyección.
- El ORM las declara con GeoAlchemy2.
