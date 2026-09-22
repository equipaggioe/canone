# ADR-0003 · Un enum se guarda como VARCHAR con CHECK

- **Estado:** Propuesta
- **Fecha:** 2026-09-22
- **Alcance:** `server/app/models/`, todos los repositorios

## Contexto

`StringEnumType()` usa `native_enum=False` para no depender del tipo `ENUM` de PostgreSQL. Desde
SQLAlchemy 1.4, `create_constraint` vale `False` por defecto: sin declararlo, la columna queda como
un TEXT sin ninguna restricción.

`validate_strings=True` solo valida del lado de Python. Todo lo que escriba por fuera del ORM —SQL
directo, una carga masiva, un job de mantenimiento, una migración— puede dejar cualquier cadena.

Hoy lo declaran banditore y concordia. navetta, presenze, vettore y cadenza no.

## Decisión

1. `StringEnumType()` incluye `create_constraint=True`, y está en el archivo canónico.
2. Los enums se declaran como `class X(str, Enum)` en `core/enums.py`. No se usa `StrEnum`, y
   `ruff` ignora `UP042` por eso.
3. No se usa el tipo `ENUM` nativo de PostgreSQL.

## Consecuencias

- La base rechaza un valor inválido escrito por cualquier vía.
- Los cuatro repositorios que hoy no lo tienen necesitan una migración que cree los CHECK. Si algún
  dato guardado no está en el enum, la migración falla: eso es el hallazgo, no un obstáculo.

## Descartado

- **El `ENUM` nativo de PostgreSQL:** agregar un valor exige `ALTER TYPE` y no se puede quitar
  ninguno, lo que convierte cada cambio de catálogo en una migración especial.
- **Validar solo en Pydantic:** deja la base sin defensa contra todo lo que no pase por la API, que
  es justo lo que hacen los scripts de carga.
