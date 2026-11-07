# ADR-0122 · Una lista del equipo lleva una identity `integer`, y no `smallint`

- **Estado:** Aceptada
- **Fecha:** 2026-11-06
- **Alcance:** [plataformas/postgres.md](../plataformas/postgres.md), `plantilla/server/src/app/models/base.py`
  y `plantilla/server/tests/test_conventions.py`

## Contexto

El [ADR-0024](0024-la-clave-primaria-se-elige-por-lo-que-guarda-la-tabla.md) daba `smallint` a una
lista del equipo cuyo tope cabe en él, y descartaba `integer`. *Integer Types* de *Data Types* dice lo
contrario: `integer` es la elección común, `smallint` se usa solo si el espacio en disco es escaso, y
`bigint`, cuando el rango de `integer` no alcanza. La página se apartaba de la fuente sin decir por qué.

## Decisión

1. Una lista propia del equipo, igual para todos los usuarios, lleva una identity `integer` si su tope
   cabe en `integer`, y `bigint` si no cabe.
2. Una clave primaria no es `smallint`.

## Consecuencias

- La clave sigue a *Integer Types* sin excepción que justificar.
- En una tabla de un millón de filas con `(bigint, <lista>, timestamptz)` o `(uuid, <lista>, text)`,
  la tabla y el índice de la clave foránea miden lo mismo con `smallint` que con `integer`, en
  PostgreSQL 17: la fila y la entrada del índice se alinean a 8 bytes.
- Una lista que crece más allá de 32 767 filas no obliga a migrar su tabla ni las claves foráneas que
  la apuntan.

## Descartado

- **`smallint`** (la regla anterior): los 2 bytes que ahorra por referencia los ocupa el relleno de
  la alineación salvo que se junten varias columnas chicas, y *Integer Types* lo deja para cuando el
  espacio en disco es escaso.
