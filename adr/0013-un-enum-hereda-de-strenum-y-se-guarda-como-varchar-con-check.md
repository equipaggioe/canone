# ADR-0013 · Un enum hereda de `StrEnum` y se guarda como `text` con CHECK

- **Estado:** Propuesta
- **Fecha:** 2026-09-23
- **Alcance:** `server/app/core/enums.py`, `server/app/models/`, todos los repositorios

## Contexto

Reemplaza al [ADR-0003](0003-enum-como-varchar-con-check.md). Se mantiene cómo se guarda un enum;
cambia la clase de la que hereda.

`class X(str, Enum)` llegó con el paso de presenze de `IntEnum` a enums de texto (2026-03-08), y de
ahí se copió a los demás. Era la forma de escribir un enum de texto, no una elección frente a
`StrEnum`: en ningún repositorio hay rastro de que se comparara. concordia agregó después
`ignore = ["UP042"]` para callar a `ruff`.

Comprobado en Python 3.13: `StringEnumType`, Pydantic, `json.dumps` y la comparación con una cadena
se comportan igual con las dos clases. Difieren solo en `str()` y en los f-strings: con
`(str, Enum)`, `f"{Status.ACTIVE}"` da `"Status.ACTIVE"`; con `StrEnum`, `"active"`.

## Decisión

1. Los enums se declaran como `class X(StrEnum)` en `core/enums.py`. `ruff` aplica `UP042`.
2. `StringEnumType()` incluye `create_constraint=True`, y está en el archivo canónico.
3. No se usa el tipo `ENUM` nativo de PostgreSQL.

## Consecuencias

- Un enum dentro de un f-string, un log o una clave de caché produce su valor, no el nombre de la
  clase.
- La base rechaza un valor inválido escrito por cualquier vía.
- En cada repositorio: cambiar la clase base de cada enum y borrar el `ignore = ["UP042"]`. Antes,
  buscar el código que dependa de que `str()` devuelva `"X.MIEMBRO"`, porque cambia de salida.
- Los repositorios que no tienen el CHECK necesitan una migración que lo cree. Si algún dato
  guardado no está en el enum, la migración falla: eso es el hallazgo, no un obstáculo.

## Descartado

- **`class X(str, Enum)` (ADR-0003):** no aporta nada que `StrEnum` no tenga, y un enum en un
  f-string produce `"X.MIEMBRO"` sin avisar.
- **El `ENUM` nativo de PostgreSQL:** agregar un valor exige `ALTER TYPE` y no se puede quitar
  ninguno, lo que convierte cada cambio de catálogo en una migración especial.
- **Validar solo en Pydantic:** deja la base sin defensa contra todo lo que no pase por la API, que
  es justo lo que hacen los scripts de carga.
